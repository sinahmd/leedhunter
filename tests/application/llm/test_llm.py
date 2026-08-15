"""
Tests for LLM abstraction and reforms
"""

import json

import pytest

from leedhunter.application.llm.arbiter import ArbitrationResult, LLMArbiter
from leedhunter.application.llm.mock import MockLLMProvider
from leedhunter.application.llm.parser import (
    LLMResponseError,
    LLMResponseParser,
    ParseStatus,
)
from leedhunter.application.llm.provider import LLMResponse, LLMUsage
from leedhunter.application.llm.schemas import (
    EntityComparisonResult,
    EntityExtractionResult,
    IntentAnalysisResult,
    LLMOpportunityItem,
    LLMSignalItem,
    OpportunityIdentificationResult,
)
from leedhunter.domain.models import Candidate, Entity


class TestLLMUsage:
    """Tests for LLMUsage"""

    def test_create_usage(self):
        """Test creating LLMUsage"""
        usage = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    def test_add_usage(self):
        """Test adding usage"""
        usage1 = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        usage2 = LLMUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300)
        combined = usage1 + usage2

        assert combined.prompt_tokens == 300
        assert combined.completion_tokens == 150
        assert combined.total_tokens == 450


class TestLLMResponse:
    """Tests for LLMResponse"""

    def test_create_response(self):
        """Test creating LLMResponse"""
        response = LLMResponse(
            content="test response",
            model="test-model",
            provider="test",
            success=True,
        )
        assert response.content == "test response"
        assert response.success is True

    def test_failed_response(self):
        """Test failed LLMResponse"""
        response = LLMResponse(
            content="",
            success=False,
            error_message="API error",
        )
        assert response.success is False
        assert response.error_message == "API error"


class TestLLMResponseParser:
    """Tests for LLMResponseParser - the main validation boundary"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = LLMResponseParser()

    def test_parse_valid_json(self):
        """Test parsing valid JSON response"""
        response = LLMResponse(
            content=json.dumps(
                {
                    "industry": "automotive",
                    "location": "mazandaran",
                    "actions": ["import"],
                    "targets": ["companies"],
                    "platforms": ["instagram"],
                    "constraints": [],
                }
            ),
            success=True,
        )
        result = self.parser.parse(response, IntentAnalysisResult)

        assert result.is_success()
        assert result.data.industry == "automotive"
        assert result.data.location == "mazandaran"

    def test_parse_json_in_code_block(self):
        """Test parsing JSON inside markdown code block"""
        json_data = json.dumps(
            {
                "industry": "automotive",
                "location": None,
                "actions": [],
                "targets": [],
                "platforms": [],
                "constraints": [],
            }
        )
        response = LLMResponse(
            content=f"```json\n{json_data}\n```",
            success=True,
        )
        result = self.parser.parse(response, IntentAnalysisResult)

        assert result.is_success()
        assert result.data.industry == "automotive"

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON"""
        response = LLMResponse(
            content="This is not JSON",
            success=True,
        )
        result = self.parser.parse(response, IntentAnalysisResult)

        assert not result.is_success()
        assert result.status == ParseStatus.JSON_ERROR

    def test_parse_validation_error(self):
        """Test parsing JSON that fails schema validation"""
        response = LLMResponse(
            content=json.dumps(
                {
                    "decision": "INVALID_DECISION",
                    "confidence": 0.5,
                }
            ),
            success=True,
        )
        result = self.parser.parse(response, EntityComparisonResult)

        assert not result.is_success()
        assert result.status == ParseStatus.VALIDATION_ERROR

    def test_parse_empty_response(self):
        """Test parsing empty response"""
        response = LLMResponse(
            content="",
            success=True,
        )
        result = self.parser.parse(response, IntentAnalysisResult)

        assert not result.is_success()
        assert result.status == ParseStatus.EMPTY_RESPONSE

    def test_parse_failed_llm_call(self):
        """Test parsing when LLM call failed"""
        response = LLMResponse(
            content="",
            success=False,
            error_message="API timeout",
        )
        result = self.parser.parse(response, IntentAnalysisResult)

        assert not result.is_success()
        assert "API timeout" in result.error_message

    def test_parse_or_raise_success(self):
        """Test parse_or_raise with valid response"""
        response = LLMResponse(
            content=json.dumps(
                {
                    "industry": "automotive",
                    "location": None,
                    "actions": [],
                    "targets": [],
                    "platforms": [],
                    "constraints": [],
                }
            ),
            success=True,
        )
        result = self.parser.parse_or_raise(response, IntentAnalysisResult)

        assert result.industry == "automotive"

    def test_parse_or_raise_failure(self):
        """Test parse_or_raise with invalid response"""
        response = LLMResponse(
            content="not json",
            success=True,
        )
        with pytest.raises(LLMResponseError):
            self.parser.parse_or_raise(response, IntentAnalysisResult)

    def test_parse_entity_comparison_valid(self):
        """Test parsing valid entity comparison"""
        response = LLMResponse(
            content=json.dumps(
                {
                    "decision": "SAME",
                    "confidence": 0.9,
                    "reasons": ["Same domain"],
                    "matched_on": ["domain"],
                    "conflicts": [],
                }
            ),
            success=True,
        )
        result = self.parser.parse(response, EntityComparisonResult)

        assert result.is_success()
        assert result.data.decision == "SAME"
        assert result.data.confidence == 0.9

    def test_parse_opportunity_result(self):
        """Test parsing opportunity identification result"""
        response = LLMResponse(
            content=json.dumps(
                {
                    "opportunities": [
                        {
                            "description": "Potential need for digital marketing",
                            "relevance_score": 0.8,
                            "evidence_ids": ["ev_1", "ev_2"],
                        }
                    ],
                    "signals": [
                        {
                            "signal_type": "expansion",
                            "description": "Expanding to new locations",
                            "confidence": 0.7,
                            "evidence_ids": ["ev_1"],
                        }
                    ],
                    "summary": "Business is expanding",
                }
            ),
            success=True,
        )
        result = self.parser.parse(response, OpportunityIdentificationResult)

        assert result.is_success()
        assert len(result.data.opportunities) == 1
        assert result.data.opportunities[0].evidence_ids == ["ev_1", "ev_2"]
        assert len(result.data.signals) == 1
        assert result.data.signals[0].signal_type == "expansion"


class TestTypedSchemas:
    """Tests for typed LLM schemas"""

    def test_llm_opportunity_item(self):
        """Test LLMOpportunityItem schema"""
        item = LLMOpportunityItem(
            description="Test opportunity",
            relevance_score=0.8,
            evidence_ids=["ev_1"],
        )
        assert item.description == "Test opportunity"
        assert item.evidence_ids == ["ev_1"]

    def test_llm_signal_item(self):
        """Test LLMSignalItem schema"""
        item = LLMSignalItem(
            signal_type="expansion",
            description="Expanding",
            confidence=0.7,
            evidence_ids=["ev_1"],
        )
        assert item.signal_type == "expansion"
        assert item.evidence_ids == ["ev_1"]

    def test_llm_signal_item_invalid_type(self):
        """Test LLMSignalItem with invalid signal type"""
        with pytest.raises(Exception):
            LLMSignalItem(
                signal_type="invalid_type",
                description="Test",
                confidence=0.5,
            )


class TestLLMArbiter:
    """Tests for LLMArbiter"""

    def test_not_available_without_llm(self):
        """Test arbiter without LLM provider"""
        arbiter = LLMArbiter(llm_provider=None)
        assert not arbiter.is_available()

    @pytest.mark.asyncio
    async def test_returns_ambiguous_without_llm(self):
        """Test returns AMBIGUOUS when no LLM available"""
        arbiter = LLMArbiter(llm_provider=None)

        candidate = Candidate(
            source="test",
            source_url="https://test.com",
            observed_name="Test",
        )
        entity = Entity(canonical_name="Test")

        result = await arbiter.arbitrate(candidate, entity)

        assert result.recommendation == "AMBIGUOUS"
        assert not result.is_llm_available
        assert not result.should_merge()

    @pytest.mark.asyncio
    async def test_arbitrate_with_valid_response(self):
        """Test arbitration with valid LLM response"""
        mock_llm = MockLLMProvider(
            responses={
                "compare": json.dumps(
                    {
                        "decision": "SAME",
                        "confidence": 0.9,
                        "reasons": ["Same domain"],
                        "matched_on": ["domain"],
                        "conflicts": [],
                    }
                ),
            },
        )
        arbiter = LLMArbiter(llm_provider=mock_llm)

        candidate = Candidate(
            source="test",
            source_url="https://example.com",
            observed_name="Test",
            observed_domain="example.com",
        )
        entity = Entity(
            canonical_name="Test",
            canonical_domain="example.com",
        )

        result = await arbiter.arbitrate(candidate, entity)

        assert result.recommendation == "SAME"
        assert result.confidence == 0.9
        assert result.is_llm_available
        assert result.should_merge()

    @pytest.mark.asyncio
    async def test_arbitrate_with_invalid_response(self):
        """Test arbitration with invalid LLM response"""
        mock_llm = MockLLMProvider(
            default_response="not json",
        )
        arbiter = LLMArbiter(llm_provider=mock_llm)

        candidate = Candidate(
            source="test",
            source_url="https://test.com",
            observed_name="Test",
        )
        entity = Entity(canonical_name="Test")

        result = await arbiter.arbitrate(candidate, entity)

        assert result.recommendation == "AMBIGUOUS"
        assert result.is_llm_available

    def test_should_merge_requires_same_and_confidence(self):
        """Test should_merge requires SAME decision and sufficient confidence"""
        result_same = ArbitrationResult(
            recommendation="SAME",
            confidence=0.9,
            reasons=[],
            matched_on=[],
            conflicts=[],
            is_llm_available=True,
        )
        assert result_same.should_merge(min_confidence=0.8)

        result_low_conf = ArbitrationResult(
            recommendation="SAME",
            confidence=0.5,
            reasons=[],
            matched_on=[],
            conflicts=[],
            is_llm_available=True,
        )
        assert not result_low_conf.should_merge(min_confidence=0.8)

        result_different = ArbitrationResult(
            recommendation="DIFFERENT",
            confidence=0.9,
            reasons=[],
            matched_on=[],
            conflicts=[],
            is_llm_available=True,
        )
        assert not result_different.should_merge()

        result_no_llm = ArbitrationResult(
            recommendation="SAME",
            confidence=0.9,
            reasons=[],
            matched_on=[],
            conflicts=[],
            is_llm_available=False,
        )
        assert not result_no_llm.should_merge()


class TestMockLLMProvider:
    """Tests for MockLLMProvider"""

    def setup_method(self):
        """Set up test fixtures"""
        self.provider = MockLLMProvider()

    def test_provider_name(self):
        """Test provider name"""
        assert self.provider.name == "mock"

    def test_provider_model(self):
        """Test provider model"""
        assert self.provider.model == "mock-model"

    @pytest.mark.asyncio
    async def test_generate(self):
        """Test generating response"""
        response = await self.provider.generate("test prompt")

        assert response.success is True
        assert response.provider == "mock"
        assert response.content is not None

    @pytest.mark.asyncio
    async def test_generate_with_custom_response(self):
        """Test generating with custom responses"""
        provider = MockLLMProvider(
            responses={"hello": '{"greeting": "world"}'},
        )
        response = await provider.generate("hello there")

        assert response.content == '{"greeting": "world"}'

    @pytest.mark.asyncio
    async def test_usage_tracking(self):
        """Test usage tracking"""
        await self.provider.generate("test prompt")
        await self.provider.generate("another prompt")

        usage = self.provider.get_total_usage()
        assert usage.total_tokens > 0
        assert self.provider.get_call_count() == 2

    @pytest.mark.asyncio
    async def test_analyze_intent(self):
        """Test intent analysis"""
        provider = MockLLMProvider(
            responses={
                "automotive": json.dumps(
                    {
                        "industry": "automotive",
                        "location": "mazandaran",
                        "actions": ["import"],
                        "targets": ["companies"],
                        "platforms": ["instagram"],
                        "constraints": [],
                    }
                ),
            },
        )
        response = await provider.analyze_intent("Find automotive importers in Mazandaran")

        assert response.success is True
        # Verify it can be parsed
        parser = LLMResponseParser()
        result = parser.parse(response, IntentAnalysisResult)
        assert result.is_success()
        assert result.data.industry == "automotive"

    @pytest.mark.asyncio
    async def test_extract_entities_evidence_scoped(self):
        """Test entity extraction is evidence-scoped"""
        provider = MockLLMProvider(
            responses={
                "test business": json.dumps(
                    {
                        "names": ["Test Business"],
                        "domains": ["test.com"],
                        "phones": ["+98 912 123 4567"],
                        "emails": ["info@test.com"],
                        "usernames": [{"platform": "instagram", "username": "test_biz"}],
                        "locations": ["Tehran"],
                    }
                ),
            },
        )
        response = await provider.extract_entities(
            "Test Business at test.com, phone +98 912 123 4567"
        )

        assert response.success is True
        parser = LLMResponseParser()
        result = parser.parse(response, EntityExtractionResult)
        assert result.is_success()

    @pytest.mark.asyncio
    async def test_compare_entities(self):
        """Test entity comparison"""
        provider = MockLLMProvider(
            responses={
                "compare": json.dumps(
                    {
                        "decision": "SAME",
                        "confidence": 0.9,
                        "reasons": ["Same domain"],
                        "matched_on": ["domain"],
                        "conflicts": [],
                    }
                ),
            },
        )
        response = await provider.compare_entities(
            {"name": "Test A", "domain": "example.com"},
            {"name": "Test B", "domain": "example.com"},
        )

        assert response.success is True
        parser = LLMResponseParser()
        result = parser.parse(response, EntityComparisonResult)
        assert result.is_success()
        assert result.data.decision == "SAME"

    def test_reset(self):
        """Test resetting usage"""
        self.provider._total_usage = LLMUsage(100, 50, 150)
        self.provider._call_count = 5

        self.provider.reset()

        assert self.provider.get_call_count() == 0
        assert self.provider.get_total_usage().total_tokens == 0

    @pytest.mark.asyncio
    async def test_full_parse_pipeline(self):
        """Test the full validation boundary: response → parse → typed result"""
        provider = MockLLMProvider(
            responses={
                "compare": json.dumps(
                    {
                        "decision": "AMBIGUOUS",
                        "confidence": 0.5,
                        "reasons": ["Similar names but different phones"],
                        "matched_on": ["name_similarity"],
                        "conflicts": ["different_phones"],
                    }
                ),
            },
        )
        parser = LLMResponseParser()

        # Step 1: Get raw response
        response = await provider.compare_entities(
            {"name": "Company A"},
            {"name": "Company B"},
        )

        # Step 2: Parse and validate
        result = parser.parse(response, EntityComparisonResult)

        # Step 3: Verify typed result
        assert result.is_success()
        data = result.get_data()
        assert data.decision == "AMBIGUOUS"
        assert data.confidence == 0.5
        assert "different_phones" in data.conflicts
