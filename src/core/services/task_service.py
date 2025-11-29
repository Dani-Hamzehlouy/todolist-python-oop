from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from src.core.config import Config
from src.core.exceptions.repository_exceptions import EntityNotFoundError, UniqueConstraintError
from src.core.exceptions.service_exceptions import InvalidTaskOperationError, ServiceError
from src.core.models.task import Task
from src.data.repository.project_repository import ProjectRepository
from src.data.repository.task_repository import TaskRepository

VALID_STATUSES = {"todo", "doing", "done"}


class TaskService:
    """Phase-2 task service orchestrating business rules for tasks."""

    def __init__(self, task_repository: TaskRepository, project_repository: ProjectRepository):
        self._task_repository = task_repository
        self._project_repository = project_repository

    def _validate_title(self, title: str) -> None:
        if not title or len(title.strip()) < 3:
            raise InvalidTaskOperationError("Task title must be at least 3 characters long.")

    def _validate_description(self, description: Optional[str]) -> None:
        if description is not None:
            text = description.strip()
            if len(text) < 10:
                raise InvalidTaskOperationError("Task description must be at least 10 characters when provided.")

    def _validate_status(self, status: str) -> None:
        if status not in VALID_STATUSES:
            raise InvalidTaskOperationError(f"Task status must be one of {', '.join(sorted(VALID_STATUSES))}.")

    def _ensure_datetime(self, value: Optional[datetime], field_name: str) -> None:
        if value is not None and not isinstance(value, datetime):
            raise InvalidTaskOperationError(f"{field_name} must be a datetime instance.")

    def _enforce_capacity(self, project_id: int) -> None:
        tasks_count = len(self._task_repository.list_by_project(project_id))
        if tasks_count >= Config.MAX_NUMBER_OF_TASK:
            raise InvalidTaskOperationError("Maximum number of tasks for this project reached.")

    def _ensure_project_exists(self, project_id: int) -> None:
        try:
            self._project_repository.get_by_id(project_id)
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc

    def create_task(
        self,
        project_id: int,
        title: str,
        description: Optional[str] = None,
        deadline: Optional[datetime] = None,
    ) -> Task:
        self._validate_title(title)
        self._validate_description(description)
        self._ensure_datetime(deadline, "Deadline")
        self._ensure_project_exists(project_id)
        self._enforce_capacity(project_id)

        try:
            return self._task_repository.create(project_id, title, description, deadline)
        except UniqueConstraintError as exc:
            raise ServiceError(str(exc)) from exc

    def list_tasks(self, project_id: int) -> List[Task]:
        self._ensure_project_exists(project_id)
        return self._task_repository.list_by_project(project_id)

    def get_task(self, task_id: int) -> Task:
        try:
            return self._task_repository.get_by_id(task_id)
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc

    def replace_task(
        self,
        task_id: int,
        title: Optional[str],
        description: Optional[str],
        status: Optional[str],
        deadline: Optional[datetime],
    ) -> Task:
        fields = {
            "title": title,
            "description": description,
            "status": status,
            "deadline": deadline,
        }
        missing = [name for name, value in fields.items() if value is None]
        if missing:
            raise ServiceError(f"Missing required fields for full replacement: {', '.join(missing)}.")

        self._validate_title(title)  # type: ignore[arg-type]
        self._validate_description(description)
        self._validate_status(status)  # type: ignore[arg-type]
        self._ensure_datetime(deadline, "Deadline")

        try:
            return self._task_repository.update(
                task_id,
                title=title,
                description=description,
                status=status,
                deadline=deadline,
            )
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc

    def update_task(
        self,
        task_id: int,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        deadline: Optional[datetime] = None,
        **extra_fields,
    ) -> Task:
        updates = {}
        if title is not None:
            self._validate_title(title)
            updates["title"] = title
        if description is not None:
            self._validate_description(description)
            updates["description"] = description
        if status is not None:
            self._validate_status(status)
            updates["status"] = status
        if deadline is not None:
            self._ensure_datetime(deadline, "Deadline")
            updates["deadline"] = deadline

        updates.update(extra_fields)

        if not updates:
            raise ServiceError("No valid fields provided for update.")

        try:
            return self._task_repository.update(task_id, **updates)
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc

    def delete_task(self, task_id: int) -> None:
        try:
            self._task_repository.delete(task_id)
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc

    def mark_task_done(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        now = datetime.utcnow()
        updates = {"status": "done", "at_closed": now}
        return self.update_task(task_id, **updates)

    def find_overdue_open_tasks(self, now: datetime) -> List[Task]:
        self._ensure_datetime(now, "Reference time")
        return self._task_repository.find_overdue_open_tasks(now)
