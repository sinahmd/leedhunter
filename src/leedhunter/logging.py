"""
Logging configuration for LeedHunter

Provides safe, structured logging without exposing sensitive information.
"""

import logging
import sys

from leedhunter.config import get_settings

# Patterns to redact from logs
SENSITIVE_PATTERNS = [
    "api_key",
    "apikey",
    "api-key",
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "cookie",
    "session",
]


def setup_logging(level: str | None = None) -> None:
    """Configure logging for the application with credential redaction"""

    if level is None:
        level = get_settings().log_level.value

    # Use SafeFormatter to prevent credential leakage
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(SafeFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    logging.basicConfig(
        level=getattr(logging, level),
        handlers=[handler],
    )

    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(f"leedhunter.{name}")


class SafeFormatter(logging.Formatter):
    """Formatter that redacts sensitive information"""

    def format(self, record: logging.LogRecord) -> str:
        """Format the record, redacting sensitive information"""
        message = super().format(record)

        # Redact sensitive information
        for pattern in SENSITIVE_PATTERNS:
            if pattern in message.lower():
                # Simple redaction - could be improved with regex
                lines = message.split("\n")
                redacted_lines = []
                for line in lines:
                    if pattern in line.lower():
                        # Find the value after the key
                        parts = line.split("=", 1)
                        if len(parts) > 1:
                            line = f"{parts[0]}=<REDACTED>"
                        parts = line.split(": ", 1)
                        if len(parts) > 1:
                            line = f"{parts[0]}: <REDACTED>"
                    redacted_lines.append(line)
                message = "\n".join(redacted_lines)

        return message


def setup_safe_logging(level: str | None = None) -> None:
    """Configure logging with sensitive data redaction"""

    if level is None:
        level = get_settings().log_level.value

    # Create handler with safe formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(SafeFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    logging.basicConfig(
        level=getattr(logging, level),
        handlers=[handler],
    )

    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
