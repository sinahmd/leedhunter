"""
Fixture Search Provider

This provider loads test fixtures from JSON files for testing and development.
It reproduces realistic noisy results including:
- Duplicates
- Different URLs
- Different names
- Persian/English variants
- Irrelevant businesses
- Same company on multiple platforms
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from leedhunter.application.search.provider import (
    ProviderHealth,
    ProviderStatus,
    SearchProvider,
    SearchResult,
)
from leedhunter.domain.models import Candidate
from leedhunter.domain.search.query import Query


def _generate_query_id(query: Query) -> str:
    """Generate a stable ID for a query"""
    content = f"{query.terms}:{query.exact_phrases}:{query.operators}"
    return f"q_{hashlib.md5(content.encode()).hexdigest()[:12]}"


class FixtureSearchProvider(SearchProvider):
    """
    Search provider that loads results from fixture files

    This provider is used for:
    - Unit testing
    - Integration testing
    - Development without real API access
    """

    def __init__(
        self,
        fixtures_dir: str | None = None,
        default_fixture: str | None = None,
    ):
        """
        Initialize fixture provider

        Args:
            fixtures_dir: Directory containing fixture files
            default_fixture: Default fixture file name to use
        """
        if fixtures_dir is None:
            self._fixtures_dir = self._find_fixtures_dir()
        else:
            self._fixtures_dir = Path(fixtures_dir)

        self._default_fixture = default_fixture
        self._loaded_fixtures: dict[str, list[dict]] = {}
        self._health = ProviderHealth(
            status=ProviderStatus.HEALTHY,
            success_rate=1.0,
        )

    @staticmethod
    def _find_fixtures_dir() -> Path:
        """
        Find the fixtures directory using multiple strategies.

        Strategy 1: Navigate from source file to project root
        Strategy 2: Search from current working directory
        Strategy 3: Use environment variable LEEDHUNTER_FIXTURES_DIR
        """
        import os

        # Strategy 1: From source file
        # src/leedhunter/application/search/providers/fixture.py → project root
        source_dir = Path(__file__).resolve()
        for parent in source_dir.parents:
            candidate = parent / "tests" / "fixtures" / "search"
            if candidate.exists() and (candidate / "default.json").exists():
                return candidate

        # Strategy 2: From current working directory
        cwd = Path.cwd()
        candidate = cwd / "tests" / "fixtures" / "search"
        if candidate.exists() and (candidate / "default.json").exists():
            return candidate

        # Strategy 3: Environment variable
        env_dir = os.environ.get("LEEDHUNTER_FIXTURES_DIR")
        if env_dir:
            candidate = Path(env_dir)
            if candidate.exists():
                return candidate

        # Fallback: return the expected path (may not exist)
        return (
            source_dir.parent.parent.parent.parent.parent.parent / "tests" / "fixtures" / "search"
        )

    @property
    def name(self) -> str:
        return "fixture"

    @property
    def supported_operators(self) -> list[str]:
        return ["site:", "intitle:", "inurl:"]

    async def search(self, query: Query) -> SearchResult:
        """
        Execute a search query using fixtures

        Args:
            query: The search query to execute

        Returns:
            SearchResult with candidates from fixtures
        """
        start_time = datetime.now(timezone.utc)

        # Determine which fixture to use
        fixture_name = self._select_fixture(query)

        # Load fixture
        fixture_data = self._load_fixture(fixture_name)

        # Convert to candidates
        candidates = self._convert_to_candidates(fixture_data, query)

        # Calculate search time
        end_time = datetime.now(timezone.utc)
        search_time = (end_time - start_time).total_seconds()

        return SearchResult(
            query=query,
            candidates=candidates,
            provider=self.name,
            total_results=len(candidates),
            search_time=search_time,
            success=True,
        )

    async def is_available(self) -> bool:
        """Check if fixture provider is available"""
        return True

    async def get_health(self) -> ProviderHealth:
        """Get provider health information"""
        return self._health

    def _select_fixture(self, query: Query) -> str:
        """
        Select which fixture to use based on query

        Args:
            query: The search query

        Returns:
            Fixture file name
        """
        # Check if we have a default fixture
        if self._default_fixture:
            return self._default_fixture

        # Try to match based on query terms
        query_text = " ".join(str(t) for t in query.terms).lower()

        # Map common terms to fixture files
        fixture_mapping = {
            "auto": "mazandaran_auto_importers.json",
            "automotive": "mazandaran_auto_importers.json",
            "خودرو": "mazandaran_auto_importers.json",
            "restaurant": "tehran_restaurants.json",
            "رستوران": "tehran_restaurants.json",
        }

        for term, fixture in fixture_mapping.items():
            if term in query_text:
                return fixture

        # Default fixture
        return "default.json"

    def _load_fixture(self, fixture_name: str) -> list[dict]:
        """
        Load fixture data from file

        Args:
            fixture_name: Name of the fixture file

        Returns:
            List of result dictionaries
        """
        # Check cache
        if fixture_name in self._loaded_fixtures:
            return self._loaded_fixtures[fixture_name]

        # Load from file
        fixture_path = self._fixtures_dir / fixture_name

        if not fixture_path.exists():
            # Return empty list if fixture doesn't exist
            return []

        with open(fixture_path, encoding="utf-8") as f:
            data = json.load(f)

        # Cache the fixture
        self._loaded_fixtures[fixture_name] = data

        return data

    def _convert_to_candidates(
        self,
        fixture_data: list[dict],
        query: Query,
    ) -> list[Candidate]:
        """
        Convert fixture data to Candidate objects

        Args:
            fixture_data: List of result dictionaries
            query: The original search query

        Returns:
            List of Candidate objects
        """
        from urllib.parse import urlparse

        candidates = []

        for item in fixture_data:
            # Validate URL before processing
            source_url = item.get("source_url", "")
            if source_url:
                try:
                    parsed = urlparse(source_url)
                    if not parsed.scheme or not parsed.netloc:
                        continue  # Skip invalid URLs
                except Exception:
                    continue  # Skip malformed URLs
            try:
                candidate = Candidate(
                    source=item.get("source", "fixture"),
                    source_url=item.get("source_url", "https://example.com"),
                    observed_name=item.get("observed_name"),
                    observed_domain=item.get("observed_domain"),
                    observed_username=item.get("observed_username"),
                    observed_phone=item.get("observed_phone"),
                    observed_email=item.get("observed_email"),
                    metadata=item.get("metadata", {}),
                    discovered_at=datetime.now(timezone.utc),
                    query_id=_generate_query_id(query),
                )
                candidates.append(candidate)
            except Exception:
                # Skip invalid entries
                continue

        return candidates

    def add_fixture(self, name: str, data: list[dict]) -> None:
        """
        Add a fixture programmatically

        Args:
            name: Fixture name
            data: Fixture data
        """
        self._loaded_fixtures[name] = data

    def clear_fixtures(self) -> None:
        """Clear all loaded fixtures"""
        self._loaded_fixtures.clear()
