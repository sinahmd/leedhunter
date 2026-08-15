"""
End-to-End Benchmark Tests

These tests verify the complete pipeline works correctly:
Search → Candidates → Entity Resolution → Evidence → Signals → Opportunities → Scoring → Lead
"""

import json
from pathlib import Path

import pytest

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
from leedhunter.application.signals.detector import SignalDetector
from leedhunter.domain.models import (
    Candidate,
    Entity,
    EntityIdentity,
    EntityIdentityType,
    Lead,
    LeadStatus,
    Opportunity,
    SearchIntent,
    Signal,
    SignalType,
)
from leedhunter.domain.search.planner import SearchPlanner


class TestEndToEndBenchmark:
    """End-to-end benchmark tests"""

    def test_full_pipeline_auto_importers(self):
        """Test full pipeline for auto importers scenario"""
        # Step 1: Intent Analysis
        intent = SearchIntent(
            objective="Find auto importers in Mazandaran",
            location="Mazandaran",
            industry="Automotive",
            constraints=["used"],
        )

        planner = SearchPlanner()
        analysis, queries = planner.plan_search(intent, max_queries=3)

        assert analysis.industry == "automotive"
        assert analysis.location == "mazandaran"
        assert len(queries) > 0

        # Step 2: Simulate search results
        raw_results = [
            {
                "source": "instagram",
                "source_url": "https://instagram.com/auto_import_maz",
                "observed_name": "واردات خودرو مازندران",
                "observed_username": "auto_import_maz",
                "observed_phone": "+98 912 123 4567",
                "metadata": {"platform": "instagram"},
            },
            {
                "source": "google",
                "source_url": "https://mazandaran-auto-import.ir",
                "observed_name": "شرکت واردات خودرو مازندران",
                "observed_domain": "mazandaran-auto-import.ir",
                "observed_email": "info@mazandaran-auto-import.ir",
                "metadata": {"platform": "website"},
            },
        ]

        # Step 3: Normalize and extract candidates
        normalizer = ResultNormalizer()
        extractor = CandidateExtractor()

        normalized = normalizer.normalize_batch(raw_results, "test", "query_1")
        extracted = extractor.extract_batch(normalized)

        assert len(extracted) == 2

        # Step 4: Deduplicate candidates
        deduplicator = CandidateDeduplicator()
        dedup_result = deduplicator.deduplicate(extracted)

        assert len(dedup_result.unique_candidates) == 2

        # Step 5: Entity Resolution
        orchestrator = EntityResolutionOrchestrator()
        entities = []

        for candidate in dedup_result.unique_candidates:
            result = orchestrator.resolve(candidate.candidate, entities)

            if result.decision == ResolutionDecision.NEW_ENTITY:
                entity = Entity(
                    id=f"entity_{len(entities) + 1}",
                    canonical_name=candidate.candidate.observed_name or "Unknown",
                    canonical_domain=candidate.candidate.observed_domain,
                    identities=[i.to_entity_identity() for i in candidate.identities],
                    metadata=candidate.candidate.metadata,
                )
                entities.append(entity)

        assert len(entities) == 2

        # Step 6: Collect evidence
        evidence_collector = EvidenceCollector()
        all_evidence = []

        for i, entity in enumerate(entities):
            # Use the extracted candidates (which are Candidate objects)
            candidate = dedup_result.unique_candidates[i].candidate
            evidence_list = evidence_collector.collect_from_candidate(
                entity.id,
                candidate,
            )
            all_evidence.extend(evidence_list)

        assert len(all_evidence) > 0

        # Step 7: Detect signals
        signal_detector = SignalDetector()
        all_signals = []

        for entity in entities:
            signals = signal_detector.detect_batch(
                entity.id,
                [e for e in all_evidence if e.entity_id == entity.id],
                entity.identities,
            )
            all_signals.extend(signals)

        assert len(all_signals) > 0

        # Step 8: Identify opportunities
        opportunity_engine = OpportunityEngine()
        all_opportunities = []

        for entity in entities:
            entity_signals = [s for s in all_signals if s.entity_id == entity.id]
            opportunities = opportunity_engine.identify(entity.id, entity_signals)
            all_opportunities.extend(opportunities)

        assert len(all_opportunities) > 0

        # Step 9: Qualify leads
        qualification_engine = QualificationEngine()
        leads = []

        for entity in entities:
            entity_signals = [s for s in all_signals if s.entity_id == entity.id]
            entity_opportunities = [o for o in all_opportunities if o.entity_id == entity.id]
            entity_evidence = [e.to_evidence() for e in all_evidence if e.entity_id == entity.id]

            lead = Lead(
                entity=entity,
                signals=entity_signals,
                opportunities=entity_opportunities,
                evidence=entity_evidence,
                score=0.0,
                status=LeadStatus.NEW,
            )

            qualification_engine.qualify_lead(lead)
            leads.append(lead)

        assert len(leads) == 2
        assert any(lead_item.status == LeadStatus.QUALIFIED for lead_item in leads)

        # Step 10: Score leads
        scoring_engine = ScoringEngine()

        for lead in leads:
            breakdown = scoring_engine.calculate_score(
                lead.entity,
                lead.signals,
                lead.opportunities,
            )
            lead.score = breakdown.total_score

        assert all(lead_item.score > 0 for lead_item in leads)

    def test_entity_resolution_accuracy(self):
        """Test entity resolution accuracy against evaluation dataset"""
        eval_path = Path(__file__).parent.parent / "evaluation" / "entity_pairs.json"

        if not eval_path.exists():
            pytest.skip("Evaluation dataset not found")

        with open(eval_path, encoding="utf-8") as f:
            pairs = json.load(f)

        orchestrator = EntityResolutionOrchestrator()

        correct = 0
        total = 0
        false_merges = 0
        false_splits = 0

        for pair in pairs:
            candidate_a = Candidate(**pair["candidate_a"])
            candidate_b = Candidate(**pair["candidate_b"])
            label = pair["label"]

            entity = Entity(
                id=f"entity_{pair['id']}",
                canonical_name=candidate_b.observed_name or "Unknown",
                canonical_domain=candidate_b.observed_domain,
            )

            result = orchestrator.resolve(candidate_a, [entity])

            if label == "SAME":
                total += 1
                if result.decision == ResolutionDecision.MATCH:
                    correct += 1
                else:
                    false_splits += 1
            elif label == "DIFFERENT":
                total += 1
                if result.decision == ResolutionDecision.NEW_ENTITY:
                    correct += 1
                else:
                    false_merges += 1

        if total > 0:
            accuracy = correct / total
            print("\nEntity Resolution Accuracy:")
            print(f"  Total pairs: {total}")
            print(f"  Correct: {correct}")
            print(f"  Accuracy: {accuracy:.2%}")
            print(f"  False merges: {false_merges}")
            print(f"  False splits: {false_splits}")

            # Assert minimum accuracy
            assert accuracy >= 0.5, f"Accuracy {accuracy:.2%} below minimum 50%"

    def test_scoring_determinism(self):
        """Test that scoring is deterministic"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            canonical_domain="example.com",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
            metadata={"industry": "automotive", "location": "mazandaran"},
        )
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.8,
            ),
        ]
        opportunities = [
            Opportunity(
                entity_id="entity_1",
                description="Partnership",
                relevance_score=0.7,
            ),
        ]

        engine = ScoringEngine()

        # Calculate score multiple times
        scores = []
        for _ in range(10):
            breakdown = engine.calculate_score(entity, signals, opportunities)
            scores.append(breakdown.total_score)

        # All scores should be identical
        assert len(set(scores)) == 1, "Scoring is not deterministic"

    def test_persian_normalization_consistency(self):
        """Test Persian normalization consistency"""
        from leedhunter.domain.normalization import (
            normalize_domain,
            normalize_phone,
            normalize_text,
        )

        # Test consistency
        text = "واردات خودرو"
        results = [normalize_text(text) for _ in range(10)]
        assert len(set(results)) == 1

        domain = "مثال.com"
        results = [normalize_domain(domain) for _ in range(10)]
        assert len(set(results)) == 1

        phone = "+98 912 123 4567"
        results = [normalize_phone(phone) for _ in range(10)]
        assert len(set(results)) == 1
