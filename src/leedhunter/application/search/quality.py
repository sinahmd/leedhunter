"""
Search Quality Loop

This module implements search quality tracking and query refinement.

It measures:
- Query effectiveness (how many candidates per query)
- Result quality (how many candidates become entities)
- Provider performance (success rate, response time)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from leedhunter.domain.search.query import Query


@dataclass
class QueryMetrics:
    """Metrics for a single query execution"""

    query: Query
    provider: str
    total_results: int = 0
    valid_candidates: int = 0
    duplicates_found: int = 0
    entities_created: int = 0
    execution_time: float = 0.0
    success: bool = True
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def effectiveness(self) -> float:
        """Query effectiveness (valid candidates / total results)"""
        if self.total_results == 0:
            return 0.0
        return self.valid_candidates / self.total_results

    @property
    def conversion_rate(self) -> float:
        """Conversion rate (entities created / valid candidates)"""
        if self.valid_candidates == 0:
            return 0.0
        return self.entities_created / self.valid_candidates


@dataclass
class ProviderMetrics:
    """Aggregated metrics for a provider"""

    provider: str
    total_queries: int = 0
    successful_queries: int = 0
    total_results: int = 0
    total_candidates: int = 0
    total_entities: int = 0
    average_execution_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Provider success rate"""
        if self.total_queries == 0:
            return 0.0
        return self.successful_queries / self.total_queries

    @property
    def average_results_per_query(self) -> float:
        """Average results per query"""
        if self.total_queries == 0:
            return 0.0
        return self.total_results / self.total_queries


@dataclass
class QualityReport:
    """Quality report for a research job"""

    total_queries: int = 0
    total_results: int = 0
    total_candidates: int = 0
    total_entities: int = 0
    average_effectiveness: float = 0.0
    provider_metrics: dict[str, ProviderMetrics] = field(default_factory=dict)
    top_queries: list[QueryMetrics] = field(default_factory=list)
    worst_queries: list[QueryMetrics] = field(default_factory=list)


class SearchQualityTracker:
    """
    Tracks search quality metrics

    This enables:
    - Measuring query effectiveness
    - Identifying best/worst performing queries
    - Provider comparison
    - Quality improvement over time
    """

    def __init__(self):
        self._query_metrics: list[QueryMetrics] = []
        self._provider_metrics: dict[str, ProviderMetrics] = {}

    def record_query(self, metrics: QueryMetrics) -> None:
        """Record metrics for a query execution"""
        self._query_metrics.append(metrics)

        # Update provider metrics
        if metrics.provider not in self._provider_metrics:
            self._provider_metrics[metrics.provider] = ProviderMetrics(
                provider=metrics.provider,
            )

        provider = self._provider_metrics[metrics.provider]
        provider.total_queries += 1
        if metrics.success:
            provider.successful_queries += 1
        provider.total_results += metrics.total_results
        provider.total_candidates += metrics.valid_candidates
        provider.total_entities += metrics.entities_created

        # Update average execution time
        n = provider.total_queries
        provider.average_execution_time = (
            provider.average_execution_time * (n - 1) + metrics.execution_time
        ) / n

    def get_provider_metrics(self, provider: str) -> ProviderMetrics | None:
        """Get metrics for a specific provider"""
        return self._provider_metrics.get(provider)

    def get_all_provider_metrics(self) -> dict[str, ProviderMetrics]:
        """Get metrics for all providers"""
        return self._provider_metrics.copy()

    def generate_report(self) -> QualityReport:
        """Generate a quality report"""
        report = QualityReport()

        if not self._query_metrics:
            return report

        report.total_queries = len(self._query_metrics)
        report.total_results = sum(m.total_results for m in self._query_metrics)
        report.total_candidates = sum(m.valid_candidates for m in self._query_metrics)
        report.total_entities = sum(m.entities_created for m in self._query_metrics)

        # Average effectiveness
        effectiveness_values = [m.effectiveness for m in self._query_metrics]
        report.average_effectiveness = (
            sum(effectiveness_values) / len(effectiveness_values) if effectiveness_values else 0.0
        )

        # Provider metrics
        report.provider_metrics = self._provider_metrics.copy()

        # Top queries (by effectiveness)
        sorted_queries = sorted(
            self._query_metrics,
            key=lambda m: m.effectiveness,
            reverse=True,
        )
        report.top_queries = sorted_queries[:5]

        # Worst queries
        report.worst_queries = sorted_queries[-5:] if len(sorted_queries) > 5 else []

        return report

    def get_query_count(self) -> int:
        """Get total number of recorded queries"""
        return len(self._query_metrics)

    def reset(self) -> None:
        """Reset all metrics"""
        self._query_metrics.clear()
        self._provider_metrics.clear()


class QueryRefiner:
    """
    Refines queries based on quality metrics

    This helps improve search results over time by:
    - Identifying ineffective queries
    - Suggesting query modifications
    - Learning from successful queries
    """

    def __init__(self):
        self._successful_patterns: list[str] = []
        self._failed_patterns: list[str] = []

    def record_outcome(
        self,
        query: Query,
        effectiveness: float,
        threshold: float = 0.5,
    ) -> None:
        """Record query outcome for learning"""
        query_str = query.to_string()

        if effectiveness >= threshold:
            if query_str not in self._successful_patterns:
                self._successful_patterns.append(query_str)
        else:
            if query_str not in self._failed_patterns:
                self._failed_patterns.append(query_str)

    def suggest_refinement(
        self,
        query: Query,
    ) -> list[str]:
        """
        Suggest refinements for a query

        Returns list of suggestions (empty if query looks good)
        """
        suggestions = []

        # Check if query has too many terms
        if len(query.terms) > 5:
            suggestions.append("Consider reducing the number of terms")

        # Check if query has exclusions
        if not query.exclusions:
            suggestions.append("Consider adding exclusions to filter irrelevant results")

        # Check if query has site operator
        if not query.has_site_operator():
            suggestions.append("Consider adding site: operator for specific platforms")

        return suggestions

    def get_successful_patterns(self) -> list[str]:
        """Get successful query patterns"""
        return self._successful_patterns.copy()

    def get_failed_patterns(self) -> list[str]:
        """Get failed query patterns"""
        return self._failed_patterns.copy()

    def reset(self) -> None:
        """Reset learned patterns"""
        self._successful_patterns.clear()
        self._failed_patterns.clear()
