from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.models.task import Task

try:  # Placeholder exception imports
    from src.core.exceptions import EntityNotFoundError, UniqueConstraintError
except ImportError:  # pragma: no cover
    class EntityNotFoundError(Exception):
        """Raised when an entity cannot be located."""

    class UniqueConstraintError(Exception):
        """Raised when a uniqueness rule is violated."""


class TaskRepository(ABC):
    """Abstract interface for task data access."""

    @abstractmethod
    def get_by_id(self, task_id: int) -> Task: ...

    @abstractmethod
    def list_by_project(self, project_id: int) -> List[Task]: ...

    @abstractmethod
    def create(self, project_id: int, title: str, description: Optional[str], deadline: Optional[datetime]) -> Task: ...

    @abstractmethod
    def update(self, task_id: int, **kwargs) -> Task: ...

    @abstractmethod
    def delete(self, task_id: int) -> None: ...

    @abstractmethod
    def find_overdue_open_tasks(self, now: datetime) -> List[Task]: ...


class SqlAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of the task repository."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, task_id: int) -> Task:
        task = self._session.get(Task, task_id)
        if task is None:
            raise EntityNotFoundError(f"Task with id {task_id} not found.")
        return task

    def list_by_project(self, project_id: int) -> List[Task]:
        stmt = select(Task).where(Task.project_id == project_id).order_by(Task.deadline)
        return list(self._session.execute(stmt).scalars().all())

    def create(
        self,
        project_id: int,
        title: str,
        description: Optional[str],
        deadline: Optional[datetime],
    ) -> Task:
        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            deadline=deadline,
        )
        self._session.add(task)
        try:
            self._session.commit()
        except Exception as exc:  # pragma: no cover - placeholder for DB constraint handling
            self._session.rollback()
            raise UniqueConstraintError("Failed to create task due to constraint violation.") from exc
        self._session.refresh(task)
        return task

    def update(self, task_id: int, **kwargs) -> Task:
        task = self.get_by_id(task_id)
        allowed_fields = {"title", "description", "status", "deadline", "at_closed"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(task, key, value)
        self._session.commit()
        self._session.refresh(task)
        return task

    def delete(self, task_id: int) -> None:
        task = self.get_by_id(task_id)
        self._session.delete(task)
        self._session.commit()

    def find_overdue_open_tasks(self, now: datetime) -> List[Task]:
        stmt = (
            select(Task)
            .where(Task.deadline.is_not(None))
            .where(Task.deadline < now)
            .where(Task.at_closed.is_(None))
            .order_by(Task.deadline)
        )
        return list(self._session.execute(stmt).scalars().all())
