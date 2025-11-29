"""Pydantic schemas describing Project payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Input model for creating a project."""

    name: str = Field(..., min_length=3, max_length=255, description="Project name (3-255 chars).")
    description: Optional[str] = Field(
        None,
        min_length=10,
        description="Optional project description with at least 10 characters.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Graduate Thesis",
                "description": "Track milestones and tasks for the thesis defense.",
            }
        }
    )


class ProjectUpdate(BaseModel):
    """Input model for partial project updates."""

    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Project name (3-255 chars).",
    )
    description: Optional[str] = Field(
        None,
        min_length=10,
        description="Optional project description with at least 10 characters.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Thesis Planning",
                "description": "Updated description with more than ten chars.",
            }
        }
    )


class ProjectResponse(BaseModel):
    """Response model returned to API clients."""

    id: int = Field(..., description="Unique project identifier.")
    name: str = Field(..., description="Project name.")
    description: Optional[str] = Field(None, description="Detailed project description, when provided.")
    created_at: Optional[datetime] = Field(None, description="Timestamp when the project was created.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Graduate Thesis",
                "description": "Track milestones and tasks for the thesis defense.",
                "created_at": "2025-01-12T09:30:00Z",
            }
        }
    )
