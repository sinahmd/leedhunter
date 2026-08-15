"""
Research Orchestrator

This module connects all components into a complete research pipeline:
1. Intent Analysis → Search Planning
2. Search Execution → Raw Results
3. Candidate Pipeline → Normalized Candidates
4. Entity Resolution → Entities
5. Evidence Collection → Evidence
6. Signal Detection → Signals
7. Opportunity Identification → Opportunities
8. Lead Qualification → Qualified Leads
9. Lead Scoring → Scored Leads
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from leedhunter.application.evidence.collector import EvidenceCollector
from leedhunter.application.opportunities.engine import OpportunityEngine
from leedhunter.application.pipeline.deduplicator import CandidateDeduplicator
from leedhunter.application.pipeline.extractor import CandidateExtractor
from leedhunter.application.pipeline.normalizer import ResultNormalizer
from leedhunter.application.qualification.engine import QualificationEngine
from leedhunter.application.resolution.orchestrator import (
    EntityResolutionOrchestrator,
    ResolutionDecision,
)
from leedhunter.application.scoring.engine import ScoringEngine
from leedhunter.application.search.provider import SearchProvider
from leedhunter.application.search.providers.fixture import FixtureSearchProvider
from leedhunter.application.signals.detector import SignalDetector
from leedhunter.application.trace.tracer import ResearchTracer, TraceEventType
from leedhunter.domain.models import (
    Candidate,
    Entity,
    EntityIdentityType,
    Lead,
    LeadStatus,
    SearchIntent,
)
from leedhunter.domain.search.planner import SearchPlanner


@dataclass
class ResearchConfig:
    """Configuration for research execution"""

    max_queries: int = 5
    max_candidates_per_query: int = 20
    max_candidates_total: int = 1000
    max_pages_per_entity: int = 10
    max_runtime_seconds: int = 3600
    max_llm_calls: int = 100
    min_score: float = 50.0
    include_signals: bool = True
    include_opportunities: bool = True


@dataclass
class ResearchResult:
    """Result of a research job"""

    research_id: str
    intent: SearchIntent
    queries_generated: int = 0
    queries_executed: int = 0
    queries_failed: int = 0
    candidates_found: int = 0
    entities_created: int = 0
    leads_qualified: int = 0
    leads: list[Lead] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    duration_seconds: float = 0.0
    success: bool = True
    partial: bool = False
    error_message: str | None = None
    budget_exceeded: bool = False
    budget_message: str | None = None
    failed_queries: list[str] = field(default_factory=list)
    coverage: dict[str, bool] = field(default_factory=dict)


class ResearchOrchestrator:
    """
    Main research orchestrator.

    Connects all components into a complete research pipeline.
    """

    def __init__(
        self,
        search_provider: SearchProvider | None = None,
        config: ResearchConfig | None = None,
    ):
        # Search
        self._search_provider = search_provider or FixtureSearchProvider()
        self._config = config or ResearchConfig()

        # Components
        self._planner = SearchPlanner()
        self._normalizer = ResultNormalizer()
        self._extractor = CandidateExtractor()
        self._deduplicator = CandidateDeduplicator()
        self._resolution = EntityResolutionOrchestrator()
        self._evidence_collector = EvidenceCollector()
        self._signal_detector = SignalDetector()
        self._opportunity_engine = OpportunityEngine()
        self._qualification_engine = QualificationEngine(min_score=self._config.min_score)
        self._scoring_engine = ScoringEngine()
        self._tracer = ResearchTracer()

    async def research(
        self,
        intent: SearchIntent,
        research_id: str | None = None,
    ) -> ResearchResult:
        """
        Execute a complete research job.

        Args:
            intent: Research intent
            research_id: Optional research ID

        Returns:
            ResearchResult with all findings
        """
        # Generate research ID
        if research_id is None:
            research_id = f"research_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        start_time = datetime.now(timezone.utc)

        # Start trace
        self._tracer.start_trace(research_id)

        result = ResearchResult(
            research_id=research_id,
            intent=intent,
        )

        try:
            # Step 1: Intent Analysis & Search Planning
            self._tracer.record_event(TraceEventType.INTENT_CREATED)
            analysis, queries = self._planner.plan_search(
                intent,
                max_queries=self._config.max_queries,
            )
            result.queries_generated = len(queries)

            # Step 2: Execute searches with budget enforcement
            all_raw_results = []
            for query in queries:
                # Check runtime budget
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                if elapsed >= self._config.max_runtime_seconds:
                    result.budget_exceeded = True
                    result.budget_message = (
                        f"Runtime budget exceeded ({self._config.max_runtime_seconds}s)"
                    )
                    self._tracer.record_event(
                        TraceEventType.ERROR_OCCURRED,
                        metadata={"error": result.budget_message},
                    )
                    break

                self._tracer.record_event(
                    TraceEventType.QUERY_EXECUTED,
                    metadata={"query": query.to_string()},
                )

                try:
                    search_result = await self._search_provider.search(query)

                    if search_result.success:
                        # Enforce per-query candidate limit
                        candidates = search_result.candidates[
                            : self._config.max_candidates_per_query
                        ]
                        all_raw_results.extend([self._candidate_to_dict(c) for c in candidates])
                        result.queries_executed += 1
                        result.coverage[query.to_string()] = True

                        # Enforce total candidate limit
                        if len(all_raw_results) >= self._config.max_candidates_total:
                            all_raw_results = all_raw_results[: self._config.max_candidates_total]
                            result.budget_exceeded = True
                            result.budget_message = (
                                f"Candidate budget exceeded ({self._config.max_candidates_total})"
                            )
                            break
                    else:
                        result.queries_failed += 1
                        result.failed_queries.append(query.to_string())
                        result.coverage[query.to_string()] = False
                        self._tracer.record_event(
                            TraceEventType.PROVIDER_FAILED,
                            metadata={
                                "query": query.to_string(),
                                "error": search_result.error_message,
                            },
                        )
                except Exception as e:
                    result.queries_failed += 1
                    result.failed_queries.append(query.to_string())
                    result.coverage[query.to_string()] = False
                    self._tracer.record_event(
                        TraceEventType.PROVIDER_FAILED,
                        metadata={"query": query.to_string(), "error": str(e)},
                    )

            result.candidates_found = len(all_raw_results)

            # Step 3: Candidate Pipeline
            normalized = self._normalizer.normalize_batch(all_raw_results, "research", research_id)
            extracted = self._extractor.extract_batch(normalized)
            dedup_result = self._deduplicator.deduplicate(extracted)

            # Step 4: Entity Resolution
            entities = []
            for candidate in dedup_result.unique_candidates:
                self._tracer.record_event(TraceEventType.CANDIDATE_CREATED)

                resolution_result = self._resolution.resolve(candidate.candidate, entities)

                if resolution_result.decision == ResolutionDecision.NEW_ENTITY:
                    entity = Entity(
                        id=f"entity_{len(entities) + 1}",
                        canonical_name=candidate.candidate.observed_name or "Unknown",
                        canonical_domain=candidate.candidate.observed_domain,
                        identities=[i.to_entity_identity() for i in candidate.identities],
                        metadata=candidate.candidate.metadata,
                    )
                    entities.append(entity)
                    self._tracer.record_event(TraceEventType.ENTITY_CREATED)
                elif resolution_result.matched_entity:
                    self._tracer.record_event(TraceEventType.ENTITY_MATCHED)

            result.entities_created = len(entities)
            result.entities = entities

            # Step 5-9: Process each entity
            leads = []
            for entity in entities:
                # Collect evidence
                evidence_list = []
                evidence_ids = []
                for extracted_candidate in dedup_result.unique_candidates:
                    if self._entity_matches_candidate(entity, extracted_candidate):
                        collected = self._evidence_collector.collect_from_candidate(
                            entity.id,
                            extracted_candidate.candidate,
                        )
                        evidence_list.extend(collected)
                        for _e in collected:
                            evidence_id = f"ev_{entity.id}_{len(evidence_ids)}"
                            evidence_ids.append(evidence_id)
                            self._tracer.record_event(TraceEventType.EVIDENCE_CREATED)

                # Convert to domain evidence
                domain_evidence = [e.to_evidence() for e in evidence_list]

                # Detect signals
                signals = []
                if self._config.include_signals:
                    signals = self._signal_detector.detect_batch(
                        entity.id,
                        domain_evidence,
                        entity.identities,
                    )
                    for _s in signals:
                        self._tracer.record_event(TraceEventType.SIGNAL_CREATED)

                # Identify opportunities
                opportunities = []
                if self._config.include_opportunities:
                    opportunities = self._opportunity_engine.identify(entity.id, signals)

                # Score lead
                breakdown = self._scoring_engine.calculate_score(entity, signals, opportunities)

                # Create lead
                lead = Lead(
                    entity=entity,
                    signals=signals,
                    opportunities=opportunities,
                    evidence=domain_evidence,
                    score=breakdown.total_score,
                    status=LeadStatus.NEW,
                )

                # Qualify lead
                self._qualification_engine.qualify_lead(lead)
                self._tracer.record_event(TraceEventType.LEAD_CREATED)
                self._tracer.record_event(
                    TraceEventType.SCORE_CALCULATED,
                    metadata={"score": breakdown.total_score},
                )

                leads.append(lead)

            # Filter qualified leads
            qualified_leads = [
                lead
                for lead in leads
                if lead.status == LeadStatus.QUALIFIED and lead.score >= self._config.min_score
            ]

            # Sort by score
            qualified_leads.sort(key=lambda lead: lead.score, reverse=True)

            result.leads = qualified_leads
            result.leads_qualified = len(qualified_leads)

            # Mark as partial if some queries failed
            if result.queries_failed > 0:
                result.partial = True
                result.success = True  # Still successful, just partial

            # End trace
            end_time = datetime.now(timezone.utc)
            result.duration_seconds = (end_time - start_time).total_seconds()
            self._tracer.end_trace(research_id, success=True)

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            self._tracer.end_trace(research_id, success=False, error_message=str(e))

        return result

    def _candidate_to_dict(self, candidate: Candidate) -> dict:
        """Convert Candidate to dictionary"""
        return {
            "source": candidate.source,
            "source_url": candidate.source_url,
            "observed_name": candidate.observed_name,
            "observed_domain": candidate.observed_domain,
            "observed_username": candidate.observed_username,
            "observed_phone": candidate.observed_phone,
            "observed_email": candidate.observed_email,
            "metadata": candidate.metadata,
        }

    def _entity_matches_candidate(self, entity: Entity, extracted) -> bool:
        """Check if entity matches extracted candidate"""
        candidate = extracted.candidate

        # Check domain match
        if entity.canonical_domain and candidate.observed_domain:
            if entity.canonical_domain.lower() == candidate.observed_domain.lower():
                return True

        # Check name match
        if entity.canonical_name and candidate.observed_name:
            if entity.canonical_name == candidate.observed_name:
                return True

        # Check identity matches
        for identity in entity.identities:
            if identity.type == EntityIdentityType.PHONE and candidate.observed_phone:
                if identity.normalized_value == candidate.observed_phone:
                    return True
            if identity.type == EntityIdentityType.EMAIL and candidate.observed_email:
                if identity.normalized_value == candidate.observed_email:
                    return True

        return False
