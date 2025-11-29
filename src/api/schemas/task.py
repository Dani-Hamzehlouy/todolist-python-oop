"""Pydantic schemas describing Task payloads."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Task status values supported by the domain."""

    PENDING = "pending"
    DOING = "doing"
    DONE = "done"


class TaskCreate(BaseModel):
    """Input payload for creating a task."""

    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    deadline: Optional[datetime]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Write literature review",
                "description": "Summarize five recent papers on the topic.",
                "deadline": "2025-01-19T12:00:00Z",
            }
        }
    )


class TaskUpdate(BaseModel):
    """Input payload for partial task updates."""

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    status: Optional[TaskStatus]
    deadline: Optional[datetime]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Draft literature review",
                "status": "doing",
                "deadline": "2025-01-20T18:00:00Z",
            }
        }
    )


class TaskResponse(BaseModel):
    """Response payload returned to API clients."""

    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    deadline: Optional[datetime]
    at_closed: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 42,
                "project_id": 1,
                "title": "Write literature review",
                "description": "Summarize five recent papers on the topic.",
                "status": "pending",
                "deadline": "2025-01-19T12:00:00Z",
                "at_closed": None,
            }
        }
    )
