"""
Input Sanitizer and Credential Redactor

This module provides security hardening:
- Input sanitization to prevent prompt injection
- Credential redaction for logs and output
- External content sanitization
"""

import re
from typing import Optional


class InputSanitizer:
    """
    Sanitizes external input to prevent prompt injection and other attacks.

    External content is treated as UNTRUSTED DATA, not instructions.
    """

    # Patterns that might indicate prompt injection attempts
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?prior\s+instructions",
        r"disregard\s+(all\s+)?previous",
        r"you\s+are\s+now\s+",
        r"act\s+as\s+",
        r"pretend\s+you\s+are",
        r"system\s*:\s*",
        r"assistant\s*:\s*",
        r"user\s*:\s*",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"\[INST\]",
        r"\[/INST\]",
    ]

    def __init__(self):
        self._injection_pattern = re.compile(
            "|".join(self.INJECTION_PATTERNS),
            re.IGNORECASE,
        )

    def sanitize_for_llm(self, text: str) -> str:
        """
        Sanitize text before sending to LLM.

        Marks external content as data, not instructions.
        """
        if not text:
            return text

        # Wrap in clear data markers
        return f"---BEGIN EXTERNAL DATA---\n{text}\n---END EXTERNAL DATA---"

    def detect_injection_attempt(self, text: str) -> bool:
        """
        Detect potential prompt injection attempts.

        Returns True if injection patterns are detected.
        """
        if not text:
            return False

        return bool(self._injection_pattern.search(text))

    def sanitize_html(self, html: str) -> str:
        """
        Sanitize HTML content.

        Removes potentially dangerous elements.
        """
        if not html:
            return html

        # Remove script tags
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)

        # Remove event handlers
        html = re.sub(r"\s+on\w+\s*=\s*[\"'][^\"']*[\"']", "", html, flags=re.IGNORECASE)

        # Remove javascript: URLs
        html = re.sub(r"javascript\s*:", "", html, flags=re.IGNORECASE)

        return html

    def sanitize_url(self, url: str) -> Optional[str]:
        """
        Sanitize and validate a URL.

        Returns sanitized URL or None if invalid.
        """
        if not url:
            return None

        url = url.strip()

        # Only allow http and https
        if not url.startswith(("http://", "https://")):
            return None

        # Basic URL validation
        if ".." in url or " " in url:
            return None

        return url


class CredentialRedactor:
    """
    Redacts credentials from text.

    Never log or expose:
    - API keys
    - Passwords
    - Tokens
    - Authorization headers
    """

    # Patterns for common credential formats
    CREDENTIAL_PATTERNS = [
        # API keys (various formats)
        (r"(api[_-]?key|apikey)\s*[:=]\s*[\"']?([a-zA-Z0-9_\-]{15,})[\"']?", r"\1=<REDACTED>"),
        # Bearer tokens
        (r"(bearer|authorization)\s*[:=]?\s*[\"']?([a-zA-Z0-9_\-\.]{20,})[\"']?", r"\1=<REDACTED>"),
        # Passwords
        (r"(password|passwd|pwd)\s*[:=]\s*[\"']?([^\s\"']{8,})[\"']?", r"\1=<REDACTED>"),
        # Generic secrets
        (r"(secret|token)\s*[:=]\s*[\"']?([a-zA-Z0-9_\-]{15,})[\"']?", r"\1=<REDACTED>"),
        # JWT tokens (any JWT pattern)
        (r"eyJ[a-zA-Z0-9_\-]*\.eyJ[a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-]*", "<JWT_REDACTED>"),
    ]

    def __init__(self):
        self._patterns = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.CREDENTIAL_PATTERNS
        ]

    def redact(self, text: str) -> str:
        """
        Redact credentials from text.

        Returns text with credentials replaced by <REDACTED>.
        """
        if not text:
            return text

        result = text
        for pattern, replacement in self._patterns:
            result = pattern.sub(replacement, result)

        return result

    def redact_dict(self, data: dict) -> dict:
        """
        Redact credentials from dictionary values.

        Returns new dict with redacted values.
        """
        redacted = {}
        sensitive_keys = {"api_key", "apikey", "password", "secret", "token", "authorization"}

        for key, value in data.items():
            if isinstance(key, str) and key.lower() in sensitive_keys:
                redacted[key] = "<REDACTED>"
            elif isinstance(value, str):
                redacted[key] = self.redact(value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_dict(value)
            else:
                redacted[key] = value

        return redacted

    def is_safe_to_log(self, text: str) -> bool:
        """
        Check if text is safe to log (no credentials).

        Returns True if no credentials detected.
        """
        redacted = self.redact(text)
        return redacted == text
