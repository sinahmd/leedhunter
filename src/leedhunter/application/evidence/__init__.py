"""
Evidence Engine module

This module implements evidence collection, validation, and management.

Every important fact must be traceable:
- source
- source_url
- query
- observed_at
- claim
- value
- confidence

Do not create unsupported factual claims.
"""

from leedhunter.application.evidence.collector import (
    EvidenceCollector,
    CollectedEvidence,
)

from leedhunter.application.evidence.validator import (
    EvidenceValidator,
    ValidationResult,
)

from leedhunter.application.evidence.deduplicator import (
    EvidenceDeduplicator,
)

__all__ = [
    # Collector
    "EvidenceCollector",
    "CollectedEvidence",
    # Validator
    "EvidenceValidator",
    "ValidationResult",
    # Deduplicator
    "EvidenceDeduplicator",
]
