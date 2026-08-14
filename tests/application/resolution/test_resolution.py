"""
Tests for entity resolution
"""

import pytest
from datetime import datetime, timezone

from leedhunter.application.resolution.orchestrator import (
    EntityResolutionOrchestrator,
    ResolutionDecision,
)
from leedhunter.application.resolution.matchers import (
    ExactMatcher,
    DeterministicMatcher,
    FuzzyMatcher,
    MatchDecision,
)
from leedhunter.domain.models import (
    Candidate,
    Entity,
    EntityIdentity,
    EntityIdentityType,
)


def create_entity(
    name: str,
    domain: str = None,
    email: str = None,
    phone: str = None,
    identities: list = None,
) -> Entity:
    """Helper to create test entity"""
    entity_id = f"entity_{hash(name)}"
    return Entity(
        id=entity_id,
        canonical_name=name,
        canonical_domain=domain,
        identities=identities or [],
    )


def create_identity(
    identity_type: EntityIdentityType,
    value: str,
    normalized_value: str = None,
) -> EntityIdentity:
    """Helper to create test identity"""
    return EntityIdentity(
        type=identity_type,
        value=value,
        normalized_value=normalized_value or value,
        source="test",
        source_url="https://test.com",
    )


class TestExactMatcher:
    """Tests for ExactMatcher"""

    def setup_method(self):
        """Set up test fixtures"""
        self.matcher = ExactMatcher()

    def test_match_by_domain(self):
        """Test matching by domain"""
        candidate = Candidate(
            source="test",
            source_url="https://example.com",
            observed_domain="example.com",
        )
        entity = create_entity("Test", domain="example.com")

        result = self.matcher.match(candidate, [entity])

        assert result is not None
        assert result.decision == MatchDecision.MATCH
        assert result.entity == entity

    def test_match_by_email(self):
        """Test matching by email"""
        candidate = Candidate(
            source="test",
            source_url="https://test.com",
            observed_email="test@example.com",
        )
        entity = create_entity(
            "Test",
            identities=[create_identity(EntityIdentityType.EMAIL, "test@example.com")],
        )

        result = self.matcher.match(candidate, [entity])

        assert result is not None
        assert result.decision == MatchDecision.MATCH

    def test_match_by_phone(self):
        """Test matching by phone"""
        candidate = Candidate(
            source="test",
            source_url="https://test.com",
            observed_phone="+98 912 123 4567",
        )
        entity = create_entity(
            "Test",
            identities=[create_identity(EntityIdentityType.PHONE, "09121234567")],
        )

        result = self.matcher.match(candidate, [entity])

        assert result is not None
        assert result.decision == MatchDecision.MATCH

    def test_no_match(self):
        """Test when no match found"""
        candidate = Candidate(
            source="test",
            source_url="https://different.com",
            observed_domain="different.com",
        )
        entity = create_entity("Test", domain="example.com")

        result = self.matcher.match(candidate, [entity])

        assert result is None


class TestDeterministicMatcher:
    """Tests for DeterministicMatcher"""

    def setup_method(self):
        """Set up test fixtures"""
        self.matcher = DeterministicMatcher()

    def test_match_normalized_domain(self):
        """Test matching normalized domain (www vs non-www)"""
        candidate = Candidate(
            source="test",
            source_url="https://www.example.com",
            observed_domain="www.example.com",
        )
        entity = create_entity("Test", domain="example.com")

        result = self.matcher.match(candidate, [entity])

        assert result is not None
        assert result.decision == MatchDecision.MATCH


class TestFuzzyMatcher:
    """Tests for FuzzyMatcher"""

    def setup_method(self):
        """Set up test fixtures"""
        self.matcher = FuzzyMatcher(threshold=0.9)

    def test_match_similar_names(self):
        """Test matching similar names"""
        candidate = Candidate(
            source="test",
            source_url="https://test.com",
            observed_name="Example Corporation",
        )
        entity = create_entity("Example Corporation")

        result = self.matcher.match(candidate, [entity])

        assert result is not None
        assert result.decision == MatchDecision.MATCH

    def test_match_persian_names(self):
        """Test matching Persian names"""
        candidate = Candidate(
            source="test",
            source_url="https://test.com",
            observed_name="شرکت واردات خودرو",
        )
        entity = create_entity("شرکت واردات خودرو")

        result = self.matcher.match(candidate, [entity])

        assert result is not None

    def test_no_match_different_names(self):
        """Test no match for different names"""
        candidate = Candidate(
            source="test",
            source_url="https://test.com",
            observed_name="Company A",
        )
        entity = create_entity("Company B")

        result = self.matcher.match(candidate, [entity])

        assert result is None


class TestEntityResolutionOrchestrator:
    """Tests for EntityResolutionOrchestrator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.orchestrator = EntityResolutionOrchestrator()

    def test_resolve_exact_match(self):
        """Test resolving with exact match"""
        candidate = Candidate(
            source="test",
            source_url="https://example.com",
            observed_domain="example.com",
        )
        entity = create_entity("Example", domain="example.com")

        result = self.orchestrator.resolve(candidate, [entity])

        assert result.decision == ResolutionDecision.MATCH
        assert result.match_stage == "exact"
        assert result.matched_entity == entity

    def test_resolve_deterministic_match(self):
        """Test resolving with deterministic match"""
        candidate = Candidate(
            source="test",
            source_url="https://example.com/path",
            observed_domain="example.com",
            observed_phone="+98 912 123 4567",
        )
        entity = create_entity(
            "Example",
            identities=[create_identity(EntityIdentityType.PHONE, "09121234567")],
        )

        result = self.orchestrator.resolve(candidate, [entity])

        assert result.decision == ResolutionDecision.MATCH
        assert result.match_stage == "exact"

    def test_resolve_fuzzy_match(self):
        """Test resolving with fuzzy match"""
        candidate = Candidate(
            source="test",
            source_url="https://test.com",
            observed_name="Example Corporation",
        )
        entity = create_entity("Example Corporation")

        result = self.orchestrator.resolve(candidate, [entity])

        assert result.decision == ResolutionDecision.MATCH
        assert result.match_stage == "fuzzy"

    def test_resolve_new_entity(self):
        """Test resolving as new entity"""
        candidate = Candidate(
            source="test",
            source_url="https://new.com",
            observed_domain="new.com",
        )
        entity = create_entity("Example", domain="example.com")

        result = self.orchestrator.resolve(candidate, [entity])

        assert result.decision == ResolutionDecision.NEW_ENTITY
        assert result.matched_entity is None

    def test_resolve_batch(self):
        """Test resolving batch of candidates"""
        candidates = [
            Candidate(source="test", source_url="https://example.com", observed_domain="example.com"),
            Candidate(source="test", source_url="https://new.com", observed_domain="new.com"),
        ]
        entity = create_entity("Example", domain="example.com")

        results = self.orchestrator.resolve_batch(candidates, [entity])

        assert len(results) == 2
        assert results[0].decision == ResolutionDecision.MATCH
        assert results[1].decision == ResolutionDecision.NEW_ENTITY

    def test_explain_resolution(self):
        """Test resolution explanation"""
        candidate = Candidate(
            source="test",
            source_url="https://example.com",
            observed_domain="example.com",
        )
        entity = create_entity("Example", domain="example.com")

        result = self.orchestrator.resolve(candidate, [entity])
        explanation = self.orchestrator.explain_resolution(result)

        assert "decision" in explanation
        assert "match_stage" in explanation
        assert "confidence" in explanation
        assert "recommendation" in explanation

    def test_evaluation_dataset(self):
        """Test against evaluation dataset"""
        import json
        from pathlib import Path

        # Load evaluation dataset
        eval_path = Path(__file__).parent.parent.parent / "evaluation" / "entity_pairs.json"
        if not eval_path.exists():
            pytest.skip("Evaluation dataset not found")

        with open(eval_path, "r", encoding="utf-8") as f:
            pairs = json.load(f)

        correct = 0
        total = 0
        false_merges = 0
        false_splits = 0

        for pair in pairs:
            candidate_a = Candidate(**pair["candidate_a"])
            candidate_b = Candidate(**pair["candidate_b"])
            label = pair["label"]

            # Create entity from candidate_b
            entity = Entity(
                id=f"entity_{pair['id']}",
                canonical_name=candidate_b.observed_name or "Unknown",
                canonical_domain=candidate_b.observed_domain,
            )

            # Try to resolve candidate_a against entity
            result = self.orchestrator.resolve(candidate_a, [entity])

            # Check result
            if label == "SAME":
                total += 1
                if result.decision == ResolutionDecision.MATCH:
                    correct += 1
                else:
                    false_splits += 1
            elif label == "DIFFERENT":
                total += 1
                if result.decision == ResolutionDecision.NEW_ENTITY:
                    correct += 1
                else:
                    false_merges += 1

        # Log results
        if total > 0:
            accuracy = correct / total
            print(f"\nEvaluation Results:")
            print(f"  Total pairs: {total}")
            print(f"  Correct: {correct}")
            print(f"  Accuracy: {accuracy:.2%}")
            print(f"  False merges: {false_merges}")
            print(f"  False splits: {false_splits}")
