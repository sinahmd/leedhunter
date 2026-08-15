"""
Evidence Validator

This module validates evidence and calculates confidence scores.

Evidence validation ensures:
- All required fields are present
- Values are valid for their type
- Confidence scores are reasonable
- Source information is complete
"""

from dataclasses import dataclass, field
from enum import Enum

from leedhunter.application.evidence.collector import CollectedEvidence
from leedhunter.domain.normalization import (
    normalize_phone,
)


class ValidationStatus(str, Enum):
    """Status of validation"""

    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ValidationResult:
    """Result of evidence validation"""

    status: ValidationStatus
    evidence: CollectedEvidence
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    adjusted_confidence: float = 1.0

    def is_valid(self) -> bool:
        """Check if evidence is valid"""
        return self.status == ValidationStatus.VALID


class EvidenceValidator:
    """
    Validates evidence and adjusts confidence scores

    Checks:
    - Required fields present
    - Value format matches claim type
    - Confidence score reasonable
    - Source information complete
    """

    def validate(self, evidence: CollectedEvidence) -> ValidationResult:
        """
        Validate evidence

        Args:
            evidence: Evidence to validate

        Returns:
            ValidationResult with status and any errors/warnings
        """
        errors = []
        warnings = []
        confidence = evidence.confidence

        # Check required fields
        if not evidence.entity_id:
            errors.append("Missing entity_id")

        if not evidence.claim:
            errors.append("Missing claim")

        if not evidence.value:
            errors.append("Missing value")

        if not evidence.source:
            warnings.append("Missing source")
            confidence *= 0.9

        if not evidence.source_url:
            warnings.append("Missing source_url")
            confidence *= 0.9

        # Validate value format based on claim type
        value_errors, value_warnings = self._validate_value(evidence.claim, evidence.value)
        errors.extend(value_errors)
        warnings.extend(value_warnings)

        # Validate confidence score
        if evidence.confidence < 0 or evidence.confidence > 1:
            errors.append(f"Invalid confidence score: {evidence.confidence}")

        if evidence.confidence < 0.5:
            warnings.append("Low confidence score")

        # Determine status
        if errors:
            status = ValidationStatus.INVALID
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.VALID

        return ValidationResult(
            status=status,
            evidence=evidence,
            errors=errors,
            warnings=warnings,
            adjusted_confidence=max(0.0, min(1.0, confidence)),
        )

    def validate_batch(
        self,
        evidence_list: list[CollectedEvidence],
    ) -> list[ValidationResult]:
        """
        Validate a batch of evidence

        Args:
            evidence_list: List of evidence to validate

        Returns:
            List of ValidationResult objects
        """
        return [self.validate(evidence) for evidence in evidence_list]

    def _validate_value(
        self,
        claim: str,
        value: str,
    ) -> tuple[list[str], list[str]]:
        """
        Validate value format based on claim type

        Args:
            claim: The claim type
            value: The value to validate

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        if claim == "phone_number":
            if not self._is_valid_phone(value):
                errors.append(f"Invalid phone number format: {value}")

        elif claim == "email_address":
            if not self._is_valid_email(value):
                errors.append(f"Invalid email format: {value}")

        elif claim == "website_domain" and not self._is_valid_domain(value):
            warnings.append(f"Unusual domain format: {value}")

        return errors, warnings

    def _is_valid_phone(self, phone: str) -> bool:
        """Check if phone number is valid"""
        normalized = normalize_phone(phone)
        if not normalized:
            return False
        # Should have at least 10 digits
        digits = "".join(c for c in normalized if c.isdigit())
        return len(digits) >= 10

    def _is_valid_email(self, email: str) -> bool:
        """Check if email is valid"""
        return "@" in email and "." in email.split("@")[-1]

    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain is valid"""
        if not domain:
            return False
        # Basic domain validation
        return "." in domain and len(domain) > 3
