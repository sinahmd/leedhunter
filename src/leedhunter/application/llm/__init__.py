"""
LLM Abstraction module

This module provides a protocol for LLM providers and related types.

LLMs are reasoning components, not databases.
LLMs may:
- analyze intent
- generate concepts
- extract semantic evidence
- compare ambiguous entities
- identify opportunities
- generate explanations

LLMs may NOT silently invent:
- business names
- phone numbers
- emails
- locations
- social profiles
- company relationships
- signals
- facts

All structured LLM output must be validated against a schema.
"""

from leedhunter.application.llm.provider import (
    LLMProvider,
    LLMResponse,
    LLMUsage,
)

from leedhunter.application.llm.errors import (
    LLMError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMProviderUnavailableError,
    LLMInvalidResponseError,
    LLMBudgetExceededError,
)

from leedhunter.application.llm.schemas import (
    IntentAnalysisResult,
    EntityExtractionResult,
    EntityComparisonResult,
    LLMOpportunityItem,
    LLMSignalItem,
    OpportunityIdentificationResult,
)

from leedhunter.application.llm.parser import (
    LLMResponseParser,
    LLMResponseError,
    ParseResult,
    ParseStatus,
)

from leedhunter.application.llm.arbiter import (
    LLMArbiter,
    ArbitrationResult,
)

from leedhunter.application.llm.mock import (
    MockLLMProvider,
)

from leedhunter.application.llm.registry import (
    LLMProviderRegistry,
    create_llm_provider_from_config,
)

__all__ = [
    # Provider
    "LLMProvider",
    "LLMResponse",
    "LLMUsage",
    # Errors
    "LLMError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMTimeoutError",
    "LLMProviderUnavailableError",
    "LLMInvalidResponseError",
    "LLMBudgetExceededError",
    # Schemas
    "IntentAnalysisResult",
    "EntityExtractionResult",
    "EntityComparisonResult",
    "LLMOpportunityItem",
    "LLMSignalItem",
    "OpportunityIdentificationResult",
    # Parser
    "LLMResponseParser",
    "LLMResponseError",
    "ParseResult",
    "ParseStatus",
    # Arbiter
    "LLMArbiter",
    "ArbitrationResult",
    # Mock
    "MockLLMProvider",
    # Registry
    "LLMProviderRegistry",
    "create_llm_provider_from_config",
]
