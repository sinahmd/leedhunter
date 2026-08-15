"""
Candidate Pipeline

This module orchestrates the candidate processing pipeline:
Search Results → Normalization → Extraction → Deduplication → Candidates
"""

from dataclasses import dataclass, field

from leedhunter.application.pipeline.deduplicator import CandidateDeduplicator, DeduplicationResult
from leedhunter.application.pipeline.extractor import CandidateExtractor, ExtractedCandidate
from leedhunter.application.pipeline.normalizer import NormalizedResult, ResultNormalizer
from leedhunter.domain.models import Candidate


@dataclass
class PipelineResult:
    """Result of the candidate pipeline"""

    # Final candidates
    candidates: list[Candidate] = field(default_factory=list)

    # Statistics
    total_raw_results: int = 0
    total_normalized: int = 0
    total_extracted: int = 0
    total_duplicates_removed: int = 0
    total_unique: int = 0

    # Detailed results
    normalized_results: list[NormalizedResult] = field(default_factory=list)
    extracted_candidates: list[ExtractedCandidate] = field(default_factory=list)
    deduplication_result: DeduplicationResult | None = None

    # Provenance
    query_id: str | None = None
    provider: str | None = None


class CandidatePipeline:
    """
    Orchestrates the candidate processing pipeline

    Steps:
    1. Normalize raw results
    2. Extract candidates and identities
    3. Deduplicate candidates
    4. Return unique candidates with provenance
    """

    def __init__(self):
        self.normalizer = ResultNormalizer()
        self.extractor = CandidateExtractor()
        self.deduplicator = CandidateDeduplicator()

    def process(
        self,
        raw_results: list[dict],
        source: str,
        query_id: str | None = None,
    ) -> PipelineResult:
        """
        Process raw results through the pipeline

        Args:
            raw_results: Raw results from search provider
            source: Source provider name
            query_id: Optional query ID for provenance

        Returns:
            PipelineResult with unique candidates and statistics
        """
        result = PipelineResult(
            total_raw_results=len(raw_results),
            query_id=query_id,
            provider=source,
        )

        # Step 1: Normalize results
        result.normalized_results = self.normalizer.normalize_batch(raw_results, source, query_id)
        result.total_normalized = len(result.normalized_results)

        # Step 2: Extract candidates
        result.extracted_candidates = self.extractor.extract_batch(result.normalized_results)
        result.total_extracted = len(result.extracted_candidates)

        # Step 3: Deduplicate candidates
        result.deduplication_result = self.deduplicator.deduplicate(result.extracted_candidates)
        result.total_duplicates_removed = result.deduplication_result.duplicates_removed
        result.total_unique = len(result.deduplication_result.unique_candidates)

        # Step 4: Convert to domain candidates
        for extracted in result.deduplication_result.unique_candidates:
            result.candidates.append(extracted.candidate)

        return result

    def process_batch(
        self,
        raw_results: list[dict],
        source: str,
        query_ids: list[str] | None = None,
    ) -> list[PipelineResult]:
        """
        Process a batch of raw results

        Args:
            raw_results: Raw results from search provider
            source: Source provider name
            query_ids: Optional list of query IDs

        Returns:
            List of PipelineResult objects
        """
        if query_ids is None:
            return [self.process(raw_results, source)]

        # Group results by query ID
        results_by_query: dict[str, list[dict]] = {}
        for i, result in enumerate(raw_results):
            query_id = query_ids[i] if i < len(query_ids) else None
            if query_id not in results_by_query:
                results_by_query[query_id] = []
            results_by_query[query_id].append(result)

        # Process each group
        return [
            self.process(results, source, query_id)
            for query_id, results in results_by_query.items()
        ]

    def merge_results(
        self,
        results: list[PipelineResult],
    ) -> PipelineResult:
        """
        Merge multiple pipeline results

        This is used when combining results from multiple queries.

        Args:
            results: List of pipeline results

        Returns:
            Merged PipelineResult
        """
        merged = PipelineResult()

        # Collect all candidates
        all_candidates = []
        for result in results:
            all_candidates.extend(result.extracted_candidates)
            merged.total_raw_results += result.total_raw_results
            merged.total_normalized += result.total_normalized
            merged.total_extracted += result.total_extracted

        # Deduplicate across all results
        dedup_result = self.deduplicator.deduplicate(all_candidates)
        merged.deduplication_result = dedup_result
        merged.total_duplicates_removed = dedup_result.duplicates_removed
        merged.total_unique = len(dedup_result.unique_candidates)

        # Convert to domain candidates
        for extracted in dedup_result.unique_candidates:
            merged.candidates.append(extracted.candidate)

        return merged
