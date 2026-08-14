"""
Candidate Pipeline module

This module implements the candidate processing pipeline:
Search Results → Normalization → Extraction → Deduplication → Candidates
"""

from leedhunter.application.pipeline.normalizer import (
    ResultNormalizer,
    NormalizedResult,
)

from leedhunter.application.pipeline.extractor import (
    CandidateExtractor,
    IdentityExtractor,
)

from leedhunter.application.pipeline.deduplicator import (
    CandidateDeduplicator,
)

from leedhunter.application.pipeline.pipeline import (
    CandidatePipeline,
)

__all__ = [
    # Normalizer
    "ResultNormalizer",
    "NormalizedResult",
    # Extractor
    "CandidateExtractor",
    "IdentityExtractor",
    # Deduplicator
    "CandidateDeduplicator",
    # Pipeline
    "CandidatePipeline",
]
