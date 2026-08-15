"""
Tests for search quality loop
"""

from leedhunter.application.search.quality import (
    ProviderMetrics,
    QueryMetrics,
    QueryRefiner,
    SearchQualityTracker,
)
from leedhunter.domain.search.query import Query, QueryTerm


class TestQueryMetrics:
    """Tests for QueryMetrics"""

    def test_create_metrics(self):
        """Test creating QueryMetrics"""
        query = Query(terms=[QueryTerm(value="test")])
        metrics = QueryMetrics(
            query=query,
            provider="test",
            total_results=10,
            valid_candidates=5,
        )

        assert metrics.total_results == 10
        assert metrics.valid_candidates == 5
        assert metrics.provider == "test"

    def test_effectiveness(self):
        """Test effectiveness calculation"""
        query = Query(terms=[QueryTerm(value="test")])
        metrics = QueryMetrics(
            query=query,
            provider="test",
            total_results=10,
            valid_candidates=5,
        )

        assert metrics.effectiveness == 0.5

    def test_effectiveness_zero_results(self):
        """Test effectiveness with zero results"""
        query = Query(terms=[QueryTerm(value="test")])
        metrics = QueryMetrics(
            query=query,
            provider="test",
            total_results=0,
            valid_candidates=0,
        )

        assert metrics.effectiveness == 0.0

    def test_conversion_rate(self):
        """Test conversion rate calculation"""
        query = Query(terms=[QueryTerm(value="test")])
        metrics = QueryMetrics(
            query=query,
            provider="test",
            total_results=10,
            valid_candidates=5,
            entities_created=2,
        )

        assert metrics.conversion_rate == 0.4


class TestProviderMetrics:
    """Tests for ProviderMetrics"""

    def test_create_metrics(self):
        """Test creating ProviderMetrics"""
        metrics = ProviderMetrics(provider="test")

        assert metrics.provider == "test"
        assert metrics.total_queries == 0

    def test_success_rate(self):
        """Test success rate calculation"""
        metrics = ProviderMetrics(
            provider="test",
            total_queries=10,
            successful_queries=8,
        )

        assert metrics.success_rate == 0.8

    def test_success_rate_zero_queries(self):
        """Test success rate with zero queries"""
        metrics = ProviderMetrics(provider="test")

        assert metrics.success_rate == 0.0

    def test_average_results_per_query(self):
        """Test average results per query"""
        metrics = ProviderMetrics(
            provider="test",
            total_queries=5,
            total_results=50,
        )

        assert metrics.average_results_per_query == 10.0


class TestSearchQualityTracker:
    """Tests for SearchQualityTracker"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tracker = SearchQualityTracker()

    def test_record_query(self):
        """Test recording a query"""
        query = Query(terms=[QueryTerm(value="test")])
        metrics = QueryMetrics(
            query=query,
            provider="test",
            total_results=10,
            valid_candidates=5,
        )

        self.tracker.record_query(metrics)

        assert self.tracker.get_query_count() == 1

    def test_provider_metrics_updated(self):
        """Test that provider metrics are updated"""
        query = Query(terms=[QueryTerm(value="test")])
        metrics = QueryMetrics(
            query=query,
            provider="test",
            total_results=10,
            valid_candidates=5,
            success=True,
        )

        self.tracker.record_query(metrics)

        provider = self.tracker.get_provider_metrics("test")
        assert provider is not None
        assert provider.total_queries == 1
        assert provider.successful_queries == 1
        assert provider.total_results == 10

    def test_multiple_queries(self):
        """Test recording multiple queries"""
        for i in range(5):
            query = Query(terms=[QueryTerm(value=f"test{i}")])
            metrics = QueryMetrics(
                query=query,
                provider="test",
                total_results=10,
                valid_candidates=5,
            )
            self.tracker.record_query(metrics)

        assert self.tracker.get_query_count() == 5

        provider = self.tracker.get_provider_metrics("test")
        assert provider.total_queries == 5

    def test_generate_report(self):
        """Test generating a quality report"""
        query = Query(terms=[QueryTerm(value="test")])
        metrics = QueryMetrics(
            query=query,
            provider="test",
            total_results=10,
            valid_candidates=5,
            entities_created=2,
        )

        self.tracker.record_query(metrics)

        report = self.tracker.generate_report()

        assert report.total_queries == 1
        assert report.total_results == 10
        assert report.total_candidates == 5
        assert report.total_entities == 2
        assert "test" in report.provider_metrics

    def test_reset(self):
        """Test resetting metrics"""
        query = Query(terms=[QueryTerm(value="test")])
        metrics = QueryMetrics(
            query=query,
            provider="test",
            total_results=10,
        )

        self.tracker.record_query(metrics)
        self.tracker.reset()

        assert self.tracker.get_query_count() == 0
        assert self.tracker.get_all_provider_metrics() == {}


class TestQueryRefiner:
    """Tests for QueryRefiner"""

    def setup_method(self):
        """Set up test fixtures"""
        self.refiner = QueryRefiner()

    def test_record_successful_outcome(self):
        """Test recording successful outcome"""
        query = Query(terms=[QueryTerm(value="test")])
        self.refiner.record_outcome(query, effectiveness=0.8)

        assert len(self.refiner.get_successful_patterns()) == 1
        assert len(self.refiner.get_failed_patterns()) == 0

    def test_record_failed_outcome(self):
        """Test recording failed outcome"""
        query = Query(terms=[QueryTerm(value="test")])
        self.refiner.record_outcome(query, effectiveness=0.2)

        assert len(self.refiner.get_successful_patterns()) == 0
        assert len(self.refiner.get_failed_patterns()) == 1

    def test_suggest_refinement_too_many_terms(self):
        """Test suggestion for too many terms"""
        query = Query(
            terms=[
                QueryTerm(value="a"),
                QueryTerm(value="b"),
                QueryTerm(value="c"),
                QueryTerm(value="d"),
                QueryTerm(value="e"),
                QueryTerm(value="f"),
            ]
        )
        suggestions = self.refiner.suggest_refinement(query)

        assert len(suggestions) > 0
        assert any("terms" in s.lower() for s in suggestions)

    def test_suggest_refinement_no_exclusions(self):
        """Test suggestion for no exclusions"""
        query = Query(terms=[QueryTerm(value="test")])
        suggestions = self.refiner.suggest_refinement(query)

        assert any("exclusion" in s.lower() for s in suggestions)

    def test_suggest_refinement_no_site(self):
        """Test suggestion for no site operator"""
        query = Query(terms=[QueryTerm(value="test")])
        suggestions = self.refiner.suggest_refinement(query)

        assert any("site" in s.lower() for s in suggestions)

    def test_reset(self):
        """Test resetting patterns"""
        query = Query(terms=[QueryTerm(value="test")])
        self.refiner.record_outcome(query, effectiveness=0.8)
        self.refiner.reset()

        assert len(self.refiner.get_successful_patterns()) == 0
        assert len(self.refiner.get_failed_patterns()) == 0
