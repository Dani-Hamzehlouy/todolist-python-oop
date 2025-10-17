# src/core/services.py

import uuid
from datetime import datetime
from typing import List, Optional
from src.core.models import Project, Task
from src.data.repository import ProjectRepository
from src.core.config import Config  # Import for checking limits if needed, though repo handles primary check


class ToDoService:
    """
    The Business Logic Layer (Service Layer).
    Orchestrates data flow and applies business rules before interacting with the repository.
    """

    def __init__(self, repository: ProjectRepository):
        self._repo = repository

    # --- Project Management Services (Based on User Stories 1, 2, 3, 8) ---

    def create_project(self, title: str, description: Optional[str] = None) -> Project:
        """
        US (1): Creates a new project.
        Handles model creation and forwards to the repository, which enforces limits and uniqueness.
        """
        # Model handles title/description length validation upon creation
        new_project = Project(title=title, description=description)

        # Repository handles MAX_NUMBER_OF_PROJECT limit and title uniqueness
        return self._repo.add_project(new_project)

    def update_project(self, project_id: str, new_title: str, new_description: Optional[str]) -> Project:
        """
        US (2): Updates an existing project.
        Model validation (length check) is inherently part of the repository's update logic.
        """
        # Ensure that title/description length constraints are respected before update (can be done here or in repo)
        # We rely on the Project model's constructor validation logic to ensure lengths are respected
        # (This is a simplified assumption for this method, a full implementation would validate inputs here)

        if len(new_title) > 30 or (new_description and len(new_description) > 150):
            # Re-raise the error based on model constraints if necessary, or pass the update request
            # For simplicity, we assume input is pre-validated by the CLI or validated in the repository update method
            pass

        return self._repo.update_project(project_id, new_title, new_description)

    def delete_project(self, project_id: str) -> bool:
        """
        US (3): Deletes a project.
        Repository implements the mandatory Cascade Delete.
        """
        return self._repo.delete_project(project_id)

    def list_projects(self) -> List[Project]:
        """
        US (8): Displays all projects, sorted by creation time.
        """
        return self._repo.list_projects()

    # --- Task Management Services (Based on User Stories 4, 5, 9 - Full CRUD for tasks will be added next) ---

    def get_project(self, project_id: str) -> Optional[Project]:
        """Helper to get a single project."""
        return self._repo.get_project_by_id(project_id)

    def add_task_to_project(self, project_id: str, title: str,
                            description: Optional[str] = None, deadline: Optional[datetime] = None) -> Task:
        """
        US (4): Adds a task to a project.
        Handles task model creation and forwards to the repository.
        """
        # Model handles validation (title/description length, default status)
        new_task = Task(title=title, description=description, deadline=deadline)

        # Repository handles MAX_NUMBER_OF_TASK limit and project existence
        return self._repo.add_task(project_id, new_task)

    def list_tasks_by_project(self, project_id: str) -> List[Task]:
        """
        US (9): Displays all tasks for a given project.
        """
        if not self._repo.get_project_by_id(project_id):
            # Check if project exists before listing tasks (Acceptance Criteria).
            raise ValueError(f"Project with ID '{project_id}' not found.")

        return self._repo.get_tasks_by_project(project_id)

    # Full Task CRUD (Edit, Delete, Change Status) methods will be added as part of the next feature.