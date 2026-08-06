"""
Base classes and types for chat tools.

This module defines the base classes and types used by all chat tools in the Avatar MCP system.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class ToolParameterType(StrEnum):
    """Types of parameters that can be accepted by a tool."""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Definition of a parameter for a tool."""

    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    default: Any | None = None
    enum: list[Any] | None = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    items: dict[str, Any] | None = None
    properties: dict[str, ToolParameter] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the parameter to a dictionary."""
        result = {
            "type": self.type.value,
            "description": self.description,
            "required": self.required,
        }

        if self.default is not None:
            result["default"] = self.default
        if self.enum is not None:
            result["enum"] = self.enum
        if self.min_value is not None:
            result["minimum"] = self.min_value
        if self.max_value is not None:
            result["maximum"] = self.max_value
        if self.items is not None:
            result["items"] = self.items
        if self.properties is not None:
            result["properties"] = {k: v.to_dict() for k, v in self.properties.items()}

        return result


class ToolExecutionStatus(StrEnum):
    """Status of a tool execution."""

    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ToolResult:
    """Result of a tool execution."""

    status: ToolExecutionStatus
    content: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(cls, content: Any, **metadata) -> ToolResult:
        """Create a successful tool result."""
        return cls(status=ToolExecutionStatus.SUCCESS, content=content, metadata=metadata)

    @classmethod
    def create_error(cls, message: str, **metadata) -> ToolResult:
        """Create an error tool result."""
        return cls(status=ToolExecutionStatus.ERROR, content=None, error=message, metadata=metadata)

    def to_dict(self) -> dict[str, Any]:
        """Convert the result to a dictionary."""
        return {
            "status": self.status.value,
            "content": self.content,
            "error": self.error,
            "metadata": self.metadata,
        }


class ToolError(Exception):
    """Base exception for tool-related errors."""

    def __init__(self, message: str, code: str = "tool_error", **kwargs):
        self.message = message
        self.code = code
        self.details = kwargs
        super().__init__(message)


class ChatTool(ABC):
    """Base class for all chat tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the tool (must be unique)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what the tool does."""
        pass

    @property
    def parameters(self) -> list[ToolParameter]:
        """Return the list of parameters this tool accepts."""
        return []

    @property
    def required_parameters(self) -> list[str]:
        """Return the list of required parameter names."""
        return [p.name for p in self.parameters if p.required]

    @property
    def schema(self) -> dict[str, Any]:
        """Return the JSON Schema for this tool."""
        params = {}
        required = []

        for param in self.parameters:
            params[param.name] = param.to_dict()
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": params, "required": required},
        }

    async def validate_parameters(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and normalize the provided parameters.

        Args:
            params: The parameters to validate

        Returns:
            The normalized parameters

        Raises:
            ToolError: If validation fails
        """
        normalized = {}

        # Check for missing required parameters
        for param in self.parameters:
            if param.required and param.name not in params:
                if param.default is not None:
                    normalized[param.name] = param.default
                else:
                    raise ToolError(f"Missing required parameter: {param.name}")

        # Validate parameter types and values
        for param in self.parameters:
            if param.name not in params and param.default is not None:
                normalized[param.name] = param.default
                continue

            if param.name not in params:
                continue

            value = params[param.name]

            # Type checking
            try:
                if param.type == ToolParameterType.STRING and not isinstance(value, str):
                    value = str(value)
                elif param.type == ToolParameterType.INTEGER:
                    value = int(value)
                elif param.type == ToolParameterType.NUMBER:
                    value = float(value)
                elif param.type == ToolParameterType.BOOLEAN:
                    if isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes", "y")
                    else:
                        value = bool(value)
                elif param.type == ToolParameterType.ARRAY and not isinstance(value, list):
                    value = [value] if value is not None else []
                elif param.type == ToolParameterType.OBJECT and not isinstance(value, dict):
                    if isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            raise ToolError(f"Parameter {param.name} must be a valid JSON object") from None
                    else:
                        value = {}
            except (ValueError, TypeError) as e:
                raise ToolError(f"Invalid value for parameter {param.name}: {e}") from e

            # Enum validation
            if param.enum and value not in param.enum:
                raise ToolError(f"Invalid value for {param.name}. Must be one of: {', '.join(map(str, param.enum))}")

            # Min/max validation for numbers
            if param.min_value is not None and value < param.min_value:
                raise ToolError(f"Value for {param.name} must be at least {param.min_value}")

            if param.max_value is not None and value > param.max_value:
                raise ToolError(f"Value for {param.name} must be at most {param.max_value}")

            normalized[param.name] = value

        return normalized

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with the given parameters.

        Args:
            **kwargs: The parameters for the tool

        Returns:
            A ToolResult containing the result of the execution
        """
        pass

    async def __call__(self, **kwargs) -> ToolResult:
        """Execute the tool with parameter validation."""
        try:
            # Validate and normalize parameters
            params = await self.validate_parameters(kwargs)

            # Execute the tool
            logger.debug(f"Executing tool {self.name} with params: {params}")
            result = await self.execute(**params)

            # Ensure the result is a ToolResult
            if not isinstance(result, ToolResult):
                result = ToolResult.success(result)

            return result

        except ToolError as e:
            logger.error(f"Tool error in {self.name}: {e}")
            return ToolResult.error(str(e), code=e.code, **e.details)

        except Exception as e:
            logger.exception(f"Unexpected error in tool {self.name}")
            return ToolResult.error(f"An unexpected error occurred: {e!s}", code="internal_error")
