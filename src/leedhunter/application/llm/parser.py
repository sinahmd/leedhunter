"""
LLM Response Parser

This module enforces the validation boundary:
raw LLM response → JSON parse → Pydantic schema validation → typed result.

Invalid output must fail explicitly.
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ValidationError

from leedhunter.application.llm.provider import LLMResponse

T = TypeVar("T", bound=BaseModel)


class ParseStatus(str, Enum):
    """Status of parsing"""

    SUCCESS = "success"
    JSON_ERROR = "json_error"
    VALIDATION_ERROR = "validation_error"
    EMPTY_RESPONSE = "empty_response"


@dataclass
class ParseResult(Generic[T]):
    """Result of parsing an LLM response"""

    status: ParseStatus
    data: Optional[T] = None
    error_message: Optional[str] = None
    raw_response: Optional[str] = None

    def is_success(self) -> bool:
        """Check if parsing was successful"""
        return self.status == ParseStatus.SUCCESS

    def get_data(self) -> T:
        """Get parsed data, raises if not successful"""
        if not self.is_success() or self.data is None:
            raise ValueError(f"Cannot get data from parse result: {self.status.value} - {self.error_message}")
        return self.data


class LLMResponseParser:
    """
    Parses and validates LLM responses against Pydantic schemas.

    Enforces the boundary:
    raw string → JSON parse → Pydantic validation → typed result

    This is the ONLY way to get typed data from LLM responses.
    """

    def parse(
        self,
        response: LLMResponse,
        schema: type[T],
    ) -> ParseResult[T]:
        """
        Parse an LLM response against a Pydantic schema

        Args:
            response: Raw LLM response
            schema: Pydantic model class to validate against

        Returns:
            ParseResult with typed data or error
        """
        # Check if response was successful
        if not response.success:
            return ParseResult(
                status=ParseStatus.VALIDATION_ERROR,
                error_message=f"LLM call failed: {response.error_message}",
                raw_response=response.content,
            )

        # Check for empty response
        if not response.content or not response.content.strip():
            return ParseResult(
                status=ParseStatus.EMPTY_RESPONSE,
                error_message="LLM returned empty response",
                raw_response=response.content,
            )

        # Try to parse JSON
        try:
            # Handle markdown code blocks
            content = response.content.strip()
            if content.startswith("```"):
                # Extract JSON from code block
                lines = content.split("\n")
                # Remove first line (```json or ```)
                lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            parsed_json = json.loads(content)
        except json.JSONDecodeError as e:
            return ParseResult(
                status=ParseStatus.JSON_ERROR,
                error_message=f"Failed to parse JSON: {e}",
                raw_response=response.content,
            )

        # Validate against schema
        try:
            validated_data = schema.model_validate(parsed_json)
            return ParseResult(
                status=ParseStatus.SUCCESS,
                data=validated_data,
                raw_response=response.content,
            )
        except ValidationError as e:
            return ParseResult(
                status=ParseStatus.VALIDATION_ERROR,
                error_message=f"Schema validation failed: {e}",
                raw_response=response.content,
            )

    def parse_or_raise(
        self,
        response: LLMResponse,
        schema: type[T],
    ) -> T:
        """
        Parse an LLM response, raising on failure

        Args:
            response: Raw LLM response
            schema: Pydantic model class to validate against

        Returns:
            Typed data

        Raises:
            LLMResponseError: If parsing fails
        """
        result = self.parse(response, schema)
        if not result.is_success():
            raise LLMResponseError(
                status=result.status,
                message=result.error_message,
                raw_response=result.raw_response,
            )
        return result.data


class LLMResponseError(Exception):
    """Error parsing LLM response"""

    def __init__(
        self,
        status: ParseStatus,
        message: str,
        raw_response: Optional[str] = None,
    ):
        self.status = status
        self.raw_response = raw_response
        super().__init__(f"LLM Response Error ({status.value}): {message}")
