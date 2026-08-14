"""
Fixture integration regression tests

These tests verify that fixture-driven research finds known candidates and leads.
"""

import pytest
from pathlib import Path

from leedhunter.domain.models import SearchIntent
from leedhunter.application.search.providers.fixture import FixtureSearchProvider
from leedhunter.application.orchestrator import ResearchOrchestrator, ResearchConfig


class TestFixtureIntegration:
    """Regression tests for fixture-driven research"""

    def test_fixture_directory_exists(self):
        """Verify fixture directory is correctly resolved"""
        provider = FixtureSearchProvider()
        fixtures_dir = provider._fixtures_dir

        assert fixtures_dir.exists(), f"Fixture directory not found: {fixtures_dir}"
        assert fixtures_dir.is_dir()

    def test_fixture_files_exist(self):
        """Verify fixture files exist"""
        provider = FixtureSearchProvider()
        fixtures_dir = provider._fixtures_dir

        expected_files = [
            "mazandaran_auto_importers.json",
            "tehran_restaurants.json",
            "default.json",
        ]

        for filename in expected_files:
            filepath = fixtures_dir / filename
            assert filepath.exists(), f"Fixture file not found: {filepath}"

    @pytest.mark.asyncio
    async def test_fixture_provider_returns_candidates(self):
        """Verify fixture provider returns candidates for matching queries"""
        provider = FixtureSearchProvider()
        from leedhunter.domain.search.query import Query, QueryTerm

        query = Query(terms=[QueryTerm(value="auto"), QueryTerm(value="mazandaran")])
        result = await provider.search(query)

        assert result.success is True
        assert len(result.candidates) > 0, "Fixture provider returned 0 candidates"

    @pytest.mark.asyncio
    async def test_research_finds_leads_from_fixtures(self):
        """Verify research orchestrator finds leads from fixture data"""
        provider = FixtureSearchProvider()
        config = ResearchConfig(max_queries=3, min_score=30.0)
        orchestrator = ResearchOrchestrator(search_provider=provider, config=config)

        intent = SearchIntent(
            objective="Find auto importers in Mazandaran",
            location="Mazandaran",
            industry="Automotive",
        )

        result = await orchestrator.research(intent)

        assert result.success is True
        assert result.candidates_found > 0, f"Expected candidates, got {result.candidates_found}"
        assert result.entities_created > 0, f"Expected entities, got {result.entities_created}"
