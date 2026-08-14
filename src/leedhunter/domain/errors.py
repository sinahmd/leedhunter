"""
Domain-specific error types

These errors represent business logic failures, not infrastructure issues.
"""


class DomainError(Exception):
    """Base exception for domain errors"""

    pass


class EntityResolutionError(DomainError):
    """Raised when entity resolution fails"""

    pass


class InvalidDataError(DomainError):
    """Raised when data validation fails"""

    pass


class ScoringError(DomainError):
    """Raised when scoring calculation fails"""

    pass
