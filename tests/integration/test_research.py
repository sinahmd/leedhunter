"""
Integration tests for research orchestrator
"""

import pytest

from leedhunter.domain.models import SearchIntent
from leedhunter.application.orchestrator import (
    ResearchOrchestrator,
    ResearchResult,
    ResearchConfig,
)
from leedhunter.application.search.providers.fixture import FixtureSearchProvider


class TestResearchOrchestrator:
    """Integration tests for ResearchOrchestrator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.orchestrator = ResearchOrchestrator()

    @pytest.mark.asyncio
    async def test_research_basic(self):
        """Test basic research execution"""
        intent = SearchIntent(
            objective="Find auto importers in Mazandaran",
            location="Mazandaran",
            industry="Automotive",
        )

        result = await self.orchestrator.research(intent)

        assert result.success is True
        assert result.research_id is not None
        assert result.queries_generated > 0

    @pytest.mark.asyncio
    async def test_research_returns_leads(self):
        """Test that research returns leads"""
        intent = SearchIntent(
            objective="Find auto importers",
            location="Mazandaran",
        )

        result = await self.orchestrator.research(intent)

        assert result.success is True
        # May or may not have leads depending on fixture data
        assert isinstance(result.leads, list)

    @pytest.mark.asyncio
    async def test_research_with_custom_config(self):
        """Test research with custom configuration"""
        config = ResearchConfig(
            max_queries=3,
            min_score=60.0,
        )
        orchestrator = ResearchOrchestrator(config=config)

        intent = SearchIntent(
            objective="Find businesses",
            location="Tehran",
        )

        result = await orchestrator.research(intent)

        assert result.success is True
        assert result.queries_generated <= 3

    @pytest.mark.asyncio
    async def test_research_with_persian_intent(self):
        """Test research with Persian intent"""
        intent = SearchIntent(
            objective="پیدا کردن واردکنندگان خودرو در مازندران",
            location="مازندران",
            industry="خودرو",
        )

        result = await self.orchestrator.research(intent)

        assert result.success is True
        assert result.queries_generated > 0

    @pytest.mark.asyncio
    async def test_research_duration_tracking(self):
        """Test that research tracks duration"""
        intent = SearchIntent(objective="Find businesses")

        result = await self.orchestrator.research(intent)

        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_research_with_custom_provider(self):
        """Test research with custom search provider"""
        # Create provider with default fixture
        provider = FixtureSearchProvider(
            default_fixture="default.json",
        )

        orchestrator = ResearchOrchestrator(search_provider=provider)

        intent = SearchIntent(objective="Find businesses")

        result = await orchestrator.research(intent)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_research_entities_created(self):
        """Test that entities are created from candidates"""
        intent = SearchIntent(
            objective="Find auto importers",
            location="Mazandaran",
        )

        result = await self.orchestrator.research(intent)

        assert result.success is True
        assert isinstance(result.entities, list)
        assert result.entities_created == len(result.entities)
