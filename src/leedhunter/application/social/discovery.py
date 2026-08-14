"""
Social Discovery

This module discovers and links social media profiles for business entities.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from leedhunter.domain.models import EntityIdentity, EntityIdentityType
from leedhunter.domain.normalization import normalize_username


class PlatformType(str, Enum):
    """Social media platform types"""

    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TELEGRAM = "telegram"


@dataclass
class SocialProfile:
    """A discovered social media profile"""

    platform: PlatformType
    username: str
    normalized_username: str
    url: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = None
    is_business: bool = False
    confidence: float = 1.0

    def to_identity(self, source: str) -> EntityIdentity:
        """Convert to domain EntityIdentity"""
        identity_type_map = {
            PlatformType.INSTAGRAM: EntityIdentityType.INSTAGRAM,
            PlatformType.LINKEDIN: EntityIdentityType.LINKEDIN,
        }
        return EntityIdentity(
            type=identity_type_map.get(self.platform, EntityIdentityType.WEBSITE),
            value=self.username,
            normalized_value=self.normalized_username,
            is_primary=False,
            is_verified=False,
            source=source,
            source_url=self.url,
        )


class SocialDiscovery:
    """
    Discovers social media profiles for business entities.

    This is a base implementation that can be extended with real API integrations.
    """

    def discover_from_username(
        self,
        username: str,
        platform: PlatformType,
    ) -> Optional[SocialProfile]:
        """
        Discover a social profile from a username

        Args:
            username: The username to look up
            platform: The platform to search

        Returns:
            SocialProfile if found, None otherwise
        """
        normalized = normalize_username(username)
        if not normalized:
            return None

        # Build URL
        url_templates = {
            PlatformType.INSTAGRAM: f"https://instagram.com/{normalized}",
            PlatformType.LINKEDIN: f"https://linkedin.com/in/{normalized}",
            PlatformType.TWITTER: f"https://twitter.com/{normalized}",
        }

        url = url_templates.get(platform, f"https://{platform.value}.com/{normalized}")

        return SocialProfile(
            platform=platform,
            username=username,
            normalized_username=normalized,
            url=url,
            confidence=0.8,
        )

    def discover_from_entity_name(
        self,
        name: str,
        platforms: Optional[list[PlatformType]] = None,
    ) -> list[SocialProfile]:
        """
        Discover social profiles from entity name

        Args:
            name: The entity name
            platforms: Platforms to search (default: all)

        Returns:
            List of discovered profiles
        """
        if platforms is None:
            platforms = [PlatformType.INSTAGRAM, PlatformType.LINKEDIN]

        profiles = []
        for platform in platforms:
            # Generate potential usernames from name
            potential_usernames = self._generate_usernames(name, platform)
            for username in potential_usernames:
                profile = self.discover_from_username(username, platform)
                if profile:
                    profiles.append(profile)

        return profiles

    def link_profiles_to_entity(
        self,
        profiles: list[SocialProfile],
        source: str,
    ) -> list[EntityIdentity]:
        """
        Convert discovered profiles to entity identities

        Args:
            profiles: Discovered social profiles
            source: Source of discovery

        Returns:
            List of EntityIdentity objects
        """
        return [profile.to_identity(source) for profile in profiles]

    def _generate_usernames(
        self,
        name: str,
        platform: PlatformType,
    ) -> list[str]:
        """Generate potential usernames from entity name"""
        # Simple username generation
        # In production, this could use LLM or more sophisticated logic
        usernames = []

        # Clean name
        clean_name = name.lower().strip()
        clean_name = clean_name.replace(" ", "_")
        clean_name = clean_name.replace("-", "_")

        usernames.append(clean_name)

        # Try without underscores
        usernames.append(clean_name.replace("_", ""))

        # Try with dots
        usernames.append(clean_name.replace("_", "."))

        return list(set(usernames))
