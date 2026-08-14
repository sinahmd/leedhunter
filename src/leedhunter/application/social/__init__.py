"""
Social Discovery module

This module implements social media profile discovery and linking.

It discovers:
- Instagram profiles
- LinkedIn profiles
- Cross-platform linking
"""

from leedhunter.application.social.discovery import (
    SocialDiscovery,
    SocialProfile,
    PlatformType,
)

__all__ = [
    "SocialDiscovery",
    "SocialProfile",
    "PlatformType",
]
