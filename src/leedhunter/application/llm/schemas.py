"""
LLM Response Schemas

This module defines Pydantic schemas for validating LLM responses.

All structured LLM output must be validated against a schema.
LLMs may NOT silently invent facts.
"""

from pydantic import BaseModel, ConfigDict, Field


class IntentAnalysisResult(BaseModel):
    """Schema for intent analysis response"""

    model_config = ConfigDict(extra="forbid")

    industry: str | None = Field(None, description="Target industry")
    location: str | None = Field(None, description="Target location")
    actions: list[str] = Field(default_factory=list, description="Desired actions")
    targets: list[str] = Field(default_factory=list, description="Target types")
    platforms: list[str] = Field(default_factory=list, description="Target platforms")
    constraints: list[str] = Field(default_factory=list, description="Constraints")


class EntityExtractionResult(BaseModel):
    """Schema for entity extraction response"""

    model_config = ConfigDict(extra="forbid")

    names: list[str] = Field(default_factory=list, description="Business names")
    domains: list[str] = Field(default_factory=list, description="Website domains")
    phones: list[str] = Field(default_factory=list, description="Phone numbers")
    emails: list[str] = Field(default_factory=list, description="Email addresses")
    usernames: list[dict[str, str]] = Field(
        default_factory=list,
        description="Social media usernames with platform",
    )
    locations: list[str] = Field(default_factory=list, description="Locations")


class EntityComparisonResult(BaseModel):
    """Schema for entity comparison response"""

    model_config = ConfigDict(extra="forbid")

    decision: str = Field(
        ...,
        description="Comparison decision: SAME, DIFFERENT, or AMBIGUOUS",
        pattern="^(SAME|DIFFERENT|AMBIGUOUS)$",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the decision",
    )
    reasons: list[str] = Field(
        default_factory=list,
        description="Reasons for the decision",
    )
    matched_on: list[str] = Field(
        default_factory=list,
        description="What matched between entities",
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="What conflicts exist",
    )


class LLMOpportunityItem(BaseModel):
    """Typed opportunity item from LLM - references evidence IDs"""

    model_config = ConfigDict(extra="forbid")

    description: str = Field(..., min_length=1, description="Opportunity description")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    evidence_ids: list[str] = Field(
        default_factory=list,
        description="Evidence IDs supporting this opportunity",
    )


class LLMSignalItem(BaseModel):
    """Typed signal item from LLM - references evidence IDs"""

    model_config = ConfigDict(extra="forbid")

    signal_type: str = Field(
        ...,
        description="Signal type (expansion, digital_presence, engagement, activity, contactability)",
        pattern="^(expansion|digital_presence|engagement|activity|contactability)$",
    )
    description: str = Field(..., min_length=1, description="Signal description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    evidence_ids: list[str] = Field(
        default_factory=list,
        description="Evidence IDs supporting this signal",
    )


class OpportunityIdentificationResult(BaseModel):
    """Schema for opportunity identification response"""

    model_config = ConfigDict(extra="forbid")

    opportunities: list[LLMOpportunityItem] = Field(
        default_factory=list,
        description="Identified opportunities",
    )
    signals: list[LLMSignalItem] = Field(
        default_factory=list,
        description="Identified signals",
    )
    summary: str = Field("", description="Summary of findings")
