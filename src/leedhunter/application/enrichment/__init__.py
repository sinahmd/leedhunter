"""
Enrichment module

This module enriches entities with additional data from web pages and profiles.
"""

from leedhunter.application.enrichment.enricher import (
    EnrichedData,
    EnrichmentResult,
    EnrichmentService,
)

__all__ = [
    "EnrichmentService",
    "EnrichmentResult",
    "EnrichedData",
]
