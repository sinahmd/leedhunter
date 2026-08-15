"""
Tests for social discovery
"""

from leedhunter.application.social.discovery import (
    PlatformType,
    SocialDiscovery,
    SocialProfile,
)
from leedhunter.domain.models import EntityIdentityType


class TestPlatformType:
    """Tests for PlatformType"""

    def test_platform_values(self):
        """Test platform type values"""
        assert PlatformType.INSTAGRAM == "instagram"
        assert PlatformType.LINKEDIN == "linkedin"
        assert PlatformType.TWITTER == "twitter"


class TestSocialProfile:
    """Tests for SocialProfile"""

    def test_create_profile(self):
        """Test creating a SocialProfile"""
        profile = SocialProfile(
            platform=PlatformType.INSTAGRAM,
            username="test_user",
            normalized_username="test_user",
            url="https://instagram.com/test_user",
        )

        assert profile.platform == PlatformType.INSTAGRAM
        assert profile.username == "test_user"
        assert profile.url == "https://instagram.com/test_user"

    def test_to_identity_instagram(self):
        """Test converting to Instagram identity"""
        profile = SocialProfile(
            platform=PlatformType.INSTAGRAM,
            username="test_user",
            normalized_username="test_user",
            url="https://instagram.com/test_user",
        )

        identity = profile.to_identity(source="test")

        assert identity.type == EntityIdentityType.INSTAGRAM
        assert identity.value == "test_user"
        assert identity.normalized_value == "test_user"
        assert identity.source == "test"
        assert identity.source_url == "https://instagram.com/test_user"

    def test_to_identity_linkedin(self):
        """Test converting to LinkedIn identity"""
        profile = SocialProfile(
            platform=PlatformType.LINKEDIN,
            username="test-user",
            normalized_username="test-user",
            url="https://linkedin.com/in/test-user",
        )

        identity = profile.to_identity(source="test")

        assert identity.type == EntityIdentityType.LINKEDIN


class TestSocialDiscovery:
    """Tests for SocialDiscovery"""

    def setup_method(self):
        """Set up test fixtures"""
        self.discovery = SocialDiscovery()

    def test_discover_from_username(self):
        """Test discovering profile from username"""
        profile = self.discovery.discover_from_username(
            "test_user",
            PlatformType.INSTAGRAM,
        )

        assert profile is not None
        assert profile.platform == PlatformType.INSTAGRAM
        assert profile.username == "test_user"
        assert profile.normalized_username == "test_user"
        assert "instagram.com" in profile.url

    def test_discover_from_username_with_at(self):
        """Test discovering profile from username with @"""
        profile = self.discovery.discover_from_username(
            "@test_user",
            PlatformType.INSTAGRAM,
        )

        assert profile is not None
        assert profile.normalized_username == "test_user"

    def test_discover_from_username_linkedin(self):
        """Test discovering LinkedIn profile"""
        profile = self.discovery.discover_from_username(
            "test-user",
            PlatformType.LINKEDIN,
        )

        assert profile is not None
        assert profile.platform == PlatformType.LINKEDIN
        assert "linkedin.com" in profile.url

    def test_discover_from_username_empty(self):
        """Test discovering with empty username"""
        profile = self.discovery.discover_from_username(
            "",
            PlatformType.INSTAGRAM,
        )

        assert profile is None

    def test_discover_from_entity_name(self):
        """Test discovering profiles from entity name"""
        profiles = self.discovery.discover_from_entity_name("Test Business")

        assert len(profiles) > 0
        platforms = [p.platform for p in profiles]
        assert PlatformType.INSTAGRAM in platforms

    def test_discover_from_entity_name_specific_platforms(self):
        """Test discovering profiles for specific platforms"""
        profiles = self.discovery.discover_from_entity_name(
            "Test Business",
            platforms=[PlatformType.INSTAGRAM],
        )

        assert len(profiles) > 0
        assert all(p.platform == PlatformType.INSTAGRAM for p in profiles)

    def test_discover_persian_name(self):
        """Test discovering profiles from Persian name"""
        profiles = self.discovery.discover_from_entity_name("شرکت تست")

        assert len(profiles) > 0

    def test_link_profiles_to_entity(self):
        """Test linking profiles to entity"""
        profiles = [
            SocialProfile(
                platform=PlatformType.INSTAGRAM,
                username="test",
                normalized_username="test",
                url="https://instagram.com/test",
            ),
            SocialProfile(
                platform=PlatformType.LINKEDIN,
                username="test",
                normalized_username="test",
                url="https://linkedin.com/in/test",
            ),
        ]

        identities = self.discovery.link_profiles_to_entity(profiles, source="test")

        assert len(identities) == 2
        assert identities[0].type == EntityIdentityType.INSTAGRAM
        assert identities[1].type == EntityIdentityType.LINKEDIN

    def test_generate_usernames(self):
        """Test username generation"""
        usernames = self.discovery._generate_usernames(
            "Test Business",
            PlatformType.INSTAGRAM,
        )

        assert len(usernames) > 0
        assert "test_business" in usernames
