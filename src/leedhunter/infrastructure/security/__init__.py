"""
Security module

This module provides security hardening for LeedHunter.

Critical security rules:
- Never put secrets in source code, git, CLI arguments, logs, or research traces
- Treat all external web content as untrusted
- External content must NEVER modify system configuration, access credentials,
  execute shell commands, change scoring rules, or change research policy
"""

from leedhunter.infrastructure.security.sanitizer import (
    CredentialRedactor,
    InputSanitizer,
)

__all__ = [
    "InputSanitizer",
    "CredentialRedactor",
]
