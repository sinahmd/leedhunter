"""
LLM Provider Protocol

This module defines the protocol for LLM providers.

Never directly couple the domain to:
- Anthropic SDK
- OpenAI SDK
- Google SDK

Create an abstraction: LLMProvider
Then implement provider adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMUsage:
    """Token usage information"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __add__(self, other: "LLMUsage") -> "LLMUsage":
        return LLMUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )


@dataclass
class LLMResponse:
    """Response from an LLM provider"""

    content: str
    usage: LLMUsage = field(default_factory=LLMUsage)
    model: str = ""
    provider: str = ""
    success: bool = True
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers

    All LLM providers must implement this interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name"""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Get the model name"""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate a response from the LLM

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation

        Returns:
            LLMResponse with generated content
        """
        pass

    async def analyze_intent(self, text: str) -> LLMResponse:
        """
        Analyze user intent from text.

        This is the primary LLM use case:
        User query → structured intent → Search Strategy.

        LLM should NOT directly perform search.
        """
        system_prompt = """You are an expert at analyzing business prospecting intents.

Extract ONLY what is explicitly stated in the user's text. Do NOT invent information.

Extract the following:
- industry: The target industry (null if not mentioned)
- location: The target location (null if not mentioned)
- actions: What actions they want to take (import, export, find, etc.)
- targets: What they're looking for (companies, businesses, etc.)
- platforms: Any specific platforms mentioned (Instagram, LinkedIn, etc.)
- constraints: Any constraints or exclusions mentioned

Return a JSON object with exactly these fields:
{
  "industry": "string or null",
  "location": "string or null",
  "actions": ["string"],
  "targets": ["string"],
  "platforms": ["string"],
  "constraints": ["string"]
}"""

        return await self.generate(
            prompt=text,
            system_prompt=system_prompt,
            temperature=0.3,
        )

    async def extract_entities(self, text: str) -> LLMResponse:
        """
        Extract entity information from text.

        EVIDENCE-SCOPED: Only extract facts present in the provided text.
        Never invent phone, email, domain, social, or location data.
        """
        system_prompt = """You are an expert at extracting business entity information.

CRITICAL RULES:
- ONLY extract information that is EXPLICITLY PRESENT in the provided text.
- Do NOT invent, guess, or hallucinate any data.
- If a field is not found in the text, use an empty list.
- Phone numbers, emails, domains must appear EXACTLY as written in the text.

Extract ONLY what exists in the text:
- names: Business names explicitly mentioned
- domains: Website domains explicitly mentioned
- phones: Phone numbers explicitly written
- emails: Email addresses explicitly written
- usernames: Social media usernames with platform (e.g., {"platform": "instagram", "username": "handle"})
- locations: Locations explicitly mentioned

Return a JSON object with exactly these fields:
{
  "names": ["string"],
  "domains": ["string"],
  "phones": ["string"],
  "emails": ["string"],
  "usernames": [{"platform": "string", "username": "string"}],
  "locations": ["string"]
}"""

        prompt = f"""Extract entity information from this text. Only extract what is explicitly present:

---BEGIN TEXT---
{text}
---END TEXT---"""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,  # Low temperature for factual extraction
        )

    async def compare_entities(
        self,
        entity_a: dict[str, Any],
        entity_b: dict[str, Any],
    ) -> LLMResponse:
        """
        Compare two entities for potential matching.

        This is used ONLY for AMBIGUOUS matches.
        LLM saying SAME must NOT directly merge entities.
        Final merge/dedup decision belongs to the deterministic Entity Resolution layer.
        """
        system_prompt = """You are an expert at comparing business entities to determine if they are the same.

RULES:
- Only consider the information provided. Do NOT invent connections.
- Names in different languages (Persian/English) for the same business = SAME
- Similar names but different domains/phones = likely DIFFERENT
- Same domain or same phone = very likely SAME
- If evidence is insufficient to decide, return AMBIGUOUS

Return a JSON object with exactly these fields:
{
  "decision": "SAME" or "DIFFERENT" or "AMBIGUOUS",
  "confidence": 0.0 to 1.0,
  "reasons": ["string explaining why"],
  "matched_on": ["what matched between them"],
  "conflicts": ["what conflicts exist"]
}"""

        prompt = f"""Compare these two entities and determine if they are the same business:

Entity A:
{entity_a}

Entity B:
{entity_b}

Are they the same business entity?"""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )

    def get_total_usage(self) -> LLMUsage:
        """
        Get total token usage

        Returns:
            LLMUsage with total usage
        """
        return LLMUsage()  # Override in subclasses to track usage
