from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.exceptions.repository_exceptions import EntityNotFoundError, UniqueConstraintError
from src.core.models.project import Project


class ProjectRepository(ABC):
    """Abstract interface for project data access."""

    @abstractmethod
    def get_by_id(self, project_id: int) -> Project: ...

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Project]: ...

    @abstractmethod
    def list_all(self) -> List[Project]: ...

    @abstractmethod
    def create(self, name: str, description: Optional[str]) -> Project: ...

    @abstractmethod
    def update(self, project_id: int, name: Optional[str], description: Optional[str]) -> Project: ...

    @abstractmethod
    def delete(self, project_id: int) -> None: ...


class SqlAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy implementation of the project repository."""

    def __init__(self, session: Session):
        self._session = session

    def _assert_unique_name(self, name: str, current_id: Optional[int] = None) -> None:
        existing = self.get_by_name(name)
        if existing and existing.id != current_id:
            raise UniqueConstraintError(f"Project with name '{name}' already exists.")

    def get_by_id(self, project_id: int) -> Project:
        project = self._session.get(Project, project_id)
        if project is None:
            raise EntityNotFoundError(f"Project with id {project_id} not found.")
        return project

    def get_by_name(self, name: str) -> Optional[Project]:
        stmt = select(Project).where(Project.name == name)
        return self._session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> List[Project]:
        stmt = select(Project).order_by(Project.created_at)
        return list(self._session.execute(stmt).scalars().all())

    def create(self, name: str, description: Optional[str]) -> Project:
        self._assert_unique_name(name)
        project = Project(name=name, description=description)
        self._session.add(project)
        self._session.commit()
        self._session.refresh(project)
        return project

    def update(self, project_id: int, name: Optional[str], description: Optional[str]) -> Project:
        project = self.get_by_id(project_id)
        if name and name != project.name:
            self._assert_unique_name(name, current_id=project_id)
            project.name = name
        if description is not None:
            project.description = description
        self._session.commit()
        self._session.refresh(project)
        return project

    def delete(self, project_id: int) -> None:
        project = self.get_by_id(project_id)
        self._session.delete(project)
        self._session.commit()
