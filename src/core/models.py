# src/core/models.py

import uuid
from datetime import datetime
from typing import Optional

# --- Constants for Business Rules ---
MAX_TITLE_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 150
VALID_TASK_STATUSES = ["todo", "doing", "done"]


class ToDoItem:
    """Base class for Project and Task to handle common properties like ID and creation time."""

    def __init__(self, title: str, description: Optional[str] = None):
        # Unique identifier for the item
        self.id = str(uuid.uuid4())
        # Time the item was created
        self.created_at = datetime.now()

        # Input validation for title (Enforces word limits - Functional Requirement)
        if not (0 < len(title) <= MAX_TITLE_LENGTH):
            raise ValueError(f"Title must be between 1 and {MAX_TITLE_LENGTH} characters.")
        self.title = title

        # Input validation for description (Functional Requirement)
        if description and len(description) > MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"Description cannot exceed {MAX_DESCRIPTION_LENGTH} characters.")
        self.description = description


class Project(ToDoItem):
    """Represents a container for tasks."""

    def __init__(self, title: str, description: Optional[str] = None):
        super().__init__(title, description)


class Task(ToDoItem):
    """Represents a single task within a project."""

    def __init__(self, title: str, description: Optional[str] = None, deadline: Optional[datetime] = None):
        super().__init__(title, description)

        # **NEW: Foreign Key** - This must be set by the repository when adding the task.
        self.project_id: Optional[str] = None

        # Default status is 'todo' (Default Behavior Acceptance Criteria) [cite: 86]
        self.status = "todo"
        self.deadline = deadline

    def change_status(self, new_status: str):
        """Changes the task's status if the new status is valid."""
        # Enforce valid statuses (Functional Requirement) [cite: 94]
        if new_status not in VALID_TASK_STATUSES:
            raise ValueError(f"Invalid status: '{new_status}'. Must be one of: {', '.join(VALID_TASK_STATUSES)}")
        self.status = new_status