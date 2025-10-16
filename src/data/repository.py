# src/data/repository.py

from typing import List, Optional
from src.core.models import Project, Task
from src.core.config import Config


class ProjectRepository:
    """
    Manages the in-memory storage for Projects and Tasks.
    Enforces business logic related to data persistence and consistency.
    """

    def __init__(self):
        # In-Memory storage using lists
        self._projects: List[Project] = []
        self._tasks: List[Task] = []

    # --- Project Methods ---

    def list_projects(self) -> List[Project]:
        """
        Retrieves all projects, sorted by creation time[cite: 115].
        """
        # Sorting by created_at time (Assumption: datetime objects can be compared)
        return sorted(self._projects, key=lambda p: p.created_at)

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Finds a project by its unique ID."""
        return next((p for p in self._projects if p.id == project_id), None)

    def get_project_by_title(self, title: str) -> Optional[Project]:
        """Checks for existing project with the same title (Acceptance Criteria)[cite: 55, 68]."""
        return next((p for p in self._projects if p.title == title), None)

    def add_project(self, project: Project) -> Project:
        """Adds a new project, checking for capacity and title uniqueness."""
        # Check MAX_NUMBER_OF_PROJECT limit (Functional Requirement)[cite: 56, 135].
        if len(self._projects) >= Config.MAX_NUMBER_OF_PROJECT:
            raise OverflowError(f"Cannot add project. Max limit of {Config.MAX_NUMBER_OF_PROJECT} reached.")

        # Check for title uniqueness (Acceptance Criteria)[cite: 55].
        if self.get_project_by_title(project.title):
            raise ValueError(f"Project with title '{project.title}' already exists.")

        self._projects.append(project)
        return project

    def update_project(self, project_id: str, new_title: str, new_description: Optional[str]) -> Project:
        """Updates a project's title and description."""
        project = self.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Project with ID '{project_id}' not found.")

        # Check if the new title is a duplicate of another project (Acceptance Criteria)[cite: 68].
        existing_project = self.get_project_by_title(new_title)
        if existing_project and existing_project.id != project_id:
            raise ValueError(f"Project with title '{new_title}' already exists.")

        project.title = new_title
        project.description = new_description
        return project

    def delete_project(self, project_id: str) -> bool:
        """
        Deletes a project and all its associated tasks (Cascade Delete)[cite: 73, 74].
        """
        initial_project_count = len(self._projects)

        # 1. Delete the project
        self._projects = [p for p in self._projects if p.id != project_id]

        # 2. Implement Cascade Delete (Mandatory Functional Requirement)[cite: 73, 75].
        tasks_before_delete = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.project_id != project_id]

        # Check if project was deleted
        if len(self._projects) < initial_project_count:
            # We don't need to check task count, as long as the project was deleted,
            # the cascade delete rule was applied to the tasks.
            return True
        return False

    # --- Task Methods ---

    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Retrieves all tasks for a specific project[cite: 124]."""
        # Note: We assume the Task object now has a 'project_id' attribute,
        # which we must ensure is set when a task is added.
        return [t for t in self._tasks if t.project_id == project_id]

    def add_task(self, project_id: str, task: Task) -> Task:
        """Adds a task to a project, checking for capacity."""
        if not self.get_project_by_id(project_id):
            raise ValueError(f"Project with ID '{project_id}' not found. Cannot add task.")

        # Check MAX_NUMBER_OF_TASK limit (Functional Requirement)[cite: 84, 135].
        if len(self.get_tasks_by_project(project_id)) >= Config.MAX_NUMBER_OF_TASK:
            raise OverflowError(f"Cannot add task. Max limit of {Config.MAX_NUMBER_OF_TASK} reached for this project.")

        # Assign the foreign key/relationship
        task.project_id = project_id
        self._tasks.append(task)
        return task

    # Additional task CRUD methods (get, update, delete) will be added later.