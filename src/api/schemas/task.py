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

    title: str = Field(..., min_length=3, max_length=255, description="Task title (3-255 chars).")
    description: Optional[str] = Field(
        None,
        min_length=10,
        description="Optional task description with at least 10 characters.",
    )
    deadline: Optional[datetime] = Field(None, description="Optional deadline (ISO 8601).")

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

    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Task title (3-255 chars).",
    )
    description: Optional[str] = Field(
        None,
        min_length=10,
        description="Optional task description with at least 10 characters.",
    )
    status: Optional[TaskStatus] = Field(
        None,
        description="Task status (pending, doing, done).",
    )
    deadline: Optional[datetime] = Field(None, description="Optional deadline (ISO 8601).")

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

    id: int = Field(..., description="Unique task identifier.")
    project_id: int = Field(..., description="Identifier of the parent project.")
    title: str = Field(..., description="Task title.")
    description: Optional[str] = Field(None, description="Extended task description, when present.")
    status: TaskStatus = Field(..., description="Current status of the task.")
    deadline: Optional[datetime] = Field(None, description="Deadline timestamp.")
    at_closed: Optional[datetime] = Field(None, description="Timestamp when task was closed, if any.")

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
