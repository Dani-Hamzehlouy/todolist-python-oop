"""Common API response envelopes."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict


class ApiResponse(BaseModel):
    """Standard envelope for successful responses."""

    status: Literal["success"]
    data: Any
    message: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": {"id": 1, "name": "Graduate Thesis"},
                "message": "Project retrieved successfully.",
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standardized error payload."""

    status: Literal["error"]
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "message": "Project with id 99 not found.",
            }
        }
    )

