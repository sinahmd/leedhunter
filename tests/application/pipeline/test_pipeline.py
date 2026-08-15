"""
Tests for candidate pipeline
"""

from leedhunter.application.pipeline.deduplicator import CandidateDeduplicator
from leedhunter.application.pipeline.extractor import CandidateExtractor, IdentityExtractor
from leedhunter.application.pipeline.normalizer import NormalizedResult, ResultNormalizer
from leedhunter.application.pipeline.pipeline import CandidatePipeline
from leedhunter.domain.models import EntityIdentityType


class TestResultNormalizer:
    """Tests for ResultNormalizer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.normalizer = ResultNormalizer()

    def test_normalize_basic_result(self):
        """Test normalizing a basic result"""
        raw = {
            "source_url": "https://example.com",
            "observed_name": "Test Business",
            "observed_domain": "example.com",
        }
        result = self.normalizer.normalize(raw, "test_source")

        assert result.source == "test_source"
        assert result.source_url == "https://example.com"
        assert result.name == "Test Business"
        assert result.domain == "example.com"

    def test_normalize_persian_result(self):
        """Test normalizing a Persian result"""
        raw = {
            "source_url": "https://example.com",
            "observed_name": "شرکت تست",
            "observed_domain": "مثال.com",
        }
        result = self.normalizer.normalize(raw, "test_source")

        assert result.name == "شرکت تست"
        assert result.name_normalized is not None
        assert result.domain == "مثال.com"

    def test_normalize_with_phone(self):
        """Test normalizing result with phone"""
        raw = {
            "source_url": "https://example.com",
            "observed_phone": "+98 912 123 4567",
        }
        result = self.normalizer.normalize(raw, "test_source")

        assert result.phone == "+98 912 123 4567"
        assert result.phone_normalized is not None

    def test_normalize_with_email(self):
        """Test normalizing result with email"""
        raw = {
            "source_url": "https://example.com",
            "observed_email": "Test@Example.com",
        }
        result = self.normalizer.normalize(raw, "test_source")

        assert result.email == "Test@Example.com"
        assert result.email_normalized == "test@example.com"

    def test_normalize_with_username(self):
        """Test normalizing result with username"""
        raw = {
            "source_url": "https://instagram.com/test_user",
            "observed_username": "test_user",
            "metadata": {"platform": "instagram"},
        }
        result = self.normalizer.normalize(raw, "test_source")

        assert result.username == "test_user"
        assert result.platform == "instagram"

    def test_normalize_batch(self):
        """Test normalizing a batch of results"""
        raw_results = [
            {"source_url": "https://example1.com", "observed_name": "Business 1"},
            {"source_url": "https://example2.com", "observed_name": "Business 2"},
        ]
        results = self.normalizer.normalize_batch(raw_results, "test_source")

        assert len(results) == 2
        assert results[0].name == "Business 1"
        assert results[1].name == "Business 2"


class TestIdentityExtractor:
    """Tests for IdentityExtractor"""

    def setup_method(self):
        """Set up test fixtures"""
        self.extractor = IdentityExtractor()

    def test_extract_domain_identity(self):
        """Test extracting domain identity"""
        result = NormalizedResult(
            source="test",
            source_url="https://example.com",
            domain="example.com",
            domain_normalized="example.com",
        )
        identities = self.extractor.extract(result)

        assert len(identities) == 1
        assert identities[0].type == EntityIdentityType.WEBSITE
        assert identities[0].value == "example.com"

    def test_extract_instagram_identity(self):
        """Test extracting Instagram identity"""
        result = NormalizedResult(
            source="test",
            source_url="https://instagram.com/test",
            username="test_user",
            username_normalized="test_user",
            platform="instagram",
        )
        identities = self.extractor.extract(result)

        assert len(identities) == 1
        assert identities[0].type == EntityIdentityType.INSTAGRAM

    def test_extract_phone_identity(self):
        """Test extracting phone identity"""
        result = NormalizedResult(
            source="test",
            source_url="https://example.com",
            phone="+98 912 123 4567",
            phone_normalized="09121234567",
        )
        identities = self.extractor.extract(result)

        assert len(identities) == 1
        assert identities[0].type == EntityIdentityType.PHONE

    def test_extract_email_identity(self):
        """Test extracting email identity"""
        result = NormalizedResult(
            source="test",
            source_url="https://example.com",
            email="test@example.com",
            email_normalized="test@example.com",
        )
        identities = self.extractor.extract(result)

        assert len(identities) == 1
        assert identities[0].type == EntityIdentityType.EMAIL

    def test_extract_multiple_identities(self):
        """Test extracting multiple identities"""
        result = NormalizedResult(
            source="test",
            source_url="https://example.com",
            domain="example.com",
            domain_normalized="example.com",
            phone="+98 912 123 4567",
            email="test@example.com",
        )
        identities = self.extractor.extract(result)

        assert len(identities) == 3


class TestCandidateExtractor:
    """Tests for CandidateExtractor"""

    def setup_method(self):
        """Set up test fixtures"""
        self.extractor = CandidateExtractor()

    def test_extract_candidate(self):
        """Test extracting a candidate"""
        result = NormalizedResult(
            source="test",
            source_url="https://example.com",
            name="Test Business",
            domain="example.com",
        )
        extracted = self.extractor.extract(result)

        assert extracted.candidate.source == "test"
        assert extracted.candidate.observed_name == "Test Business"
        assert extracted.confidence > 0

    def test_extract_confidence(self):
        """Test confidence calculation"""
        # High confidence result
        result = NormalizedResult(
            source="test",
            source_url="https://example.com",
            name="Test Business",
            domain="example.com",
            phone="+98 912 123 4567",
            email="test@example.com",
        )
        extracted = self.extractor.extract(result)
        assert extracted.confidence > 0.5

        # Low confidence result
        result_low = NormalizedResult(
            source="test",
            source_url="https://example.com",
        )
        extracted_low = self.extractor.extract(result_low)
        assert extracted_low.confidence < extracted.confidence


class TestCandidateDeduplicator:
    """Tests for CandidateDeduplicator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.deduplicator = CandidateDeduplicator()

    def test_deduplicate_by_domain(self):
        """Test deduplication by domain"""
        from leedhunter.application.pipeline.extractor import ExtractedCandidate, ExtractedIdentity
        from leedhunter.domain.models import Candidate, EntityIdentityType

        # Create two candidates with same domain
        candidate1 = ExtractedCandidate(
            candidate=Candidate(source="test", source_url="https://example.com"),
            identities=[
                ExtractedIdentity(
                    type=EntityIdentityType.WEBSITE,
                    value="example.com",
                    normalized_value="example.com",
                    source="test",
                    source_url="https://example.com",
                )
            ],
        )
        candidate2 = ExtractedCandidate(
            candidate=Candidate(source="test", source_url="https://www.example.com"),
            identities=[
                ExtractedIdentity(
                    type=EntityIdentityType.WEBSITE,
                    value="www.example.com",
                    normalized_value="example.com",
                    source="test",
                    source_url="https://www.example.com",
                )
            ],
        )

        result = self.deduplicator.deduplicate([candidate1, candidate2])

        assert result.duplicates_removed == 1
        assert len(result.unique_candidates) == 1

    def test_deduplicate_by_email(self):
        """Test deduplication by email"""
        from leedhunter.application.pipeline.extractor import ExtractedCandidate, ExtractedIdentity
        from leedhunter.domain.models import Candidate, EntityIdentityType

        candidate1 = ExtractedCandidate(
            candidate=Candidate(source="test", source_url="https://example1.com"),
            identities=[
                ExtractedIdentity(
                    type=EntityIdentityType.EMAIL,
                    value="test@example.com",
                    normalized_value="test@example.com",
                    source="test",
                    source_url="https://example1.com",
                )
            ],
        )
        candidate2 = ExtractedCandidate(
            candidate=Candidate(source="test", source_url="https://example2.com"),
            identities=[
                ExtractedIdentity(
                    type=EntityIdentityType.EMAIL,
                    value="test@example.com",
                    normalized_value="test@example.com",
                    source="test",
                    source_url="https://example2.com",
                )
            ],
        )

        result = self.deduplicator.deduplicate([candidate1, candidate2])

        assert result.duplicates_removed == 1
        assert len(result.unique_candidates) == 1

    def test_no_duplicates(self):
        """Test with no duplicates"""
        from leedhunter.application.pipeline.extractor import ExtractedCandidate, ExtractedIdentity
        from leedhunter.domain.models import Candidate, EntityIdentityType

        candidate1 = ExtractedCandidate(
            candidate=Candidate(source="test", source_url="https://example1.com"),
            identities=[
                ExtractedIdentity(
                    type=EntityIdentityType.WEBSITE,
                    value="example1.com",
                    normalized_value="example1.com",
                    source="test",
                    source_url="https://example1.com",
                )
            ],
        )
        candidate2 = ExtractedCandidate(
            candidate=Candidate(source="test", source_url="https://example2.com"),
            identities=[
                ExtractedIdentity(
                    type=EntityIdentityType.WEBSITE,
                    value="example2.com",
                    normalized_value="example2.com",
                    source="test",
                    source_url="https://example2.com",
                )
            ],
        )

        result = self.deduplicator.deduplicate([candidate1, candidate2])

        assert result.duplicates_removed == 0
        assert len(result.unique_candidates) == 2


class TestCandidatePipeline:
    """Tests for CandidatePipeline"""

    def setup_method(self):
        """Set up test fixtures"""
        self.pipeline = CandidatePipeline()

    def test_process_basic_results(self):
        """Test processing basic results"""
        raw_results = [
            {
                "source_url": "https://example.com",
                "observed_name": "Test Business",
                "observed_domain": "example.com",
            },
        ]
        result = self.pipeline.process(raw_results, "test_source")

        assert result.total_raw_results == 1
        assert result.total_normalized == 1
        assert result.total_extracted == 1
        assert len(result.candidates) == 1

    def test_process_with_duplicates(self):
        """Test processing results with duplicates"""
        raw_results = [
            {
                "source_url": "https://example.com",
                "observed_name": "Test Business",
                "observed_domain": "example.com",
            },
            {
                "source_url": "https://www.example.com",
                "observed_name": "Test Business",
                "observed_domain": "www.example.com",
            },
        ]
        result = self.pipeline.process(raw_results, "test_source")

        assert result.total_raw_results == 2
        assert result.total_duplicates_removed == 1
        assert len(result.candidates) == 1

    def test_process_persian_results(self):
        """Test processing Persian results"""
        raw_results = [
            {
                "source_url": "https://example.com",
                "observed_name": "شرکت تست",
                "observed_domain": "مثال.com",
            },
        ]
        result = self.pipeline.process(raw_results, "test_source")

        assert len(result.candidates) == 1
        assert result.candidates[0].observed_name == "شرکت تست"

    def test_merge_results(self):
        """Test merging multiple results"""
        raw_results1 = [
            {"source_url": "https://example1.com", "observed_domain": "example1.com"},
        ]
        raw_results2 = [
            {"source_url": "https://example2.com", "observed_domain": "example2.com"},
        ]

        result1 = self.pipeline.process(raw_results1, "test")
        result2 = self.pipeline.process(raw_results2, "test")

        merged = self.pipeline.merge_results([result1, result2])

        assert len(merged.candidates) == 2
