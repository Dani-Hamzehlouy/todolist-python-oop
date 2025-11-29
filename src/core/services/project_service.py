from __future__ import annotations

from typing import List, Optional

from src.core.config import Config
from src.core.exceptions.repository_exceptions import (
    EntityNotFoundError,
    UniqueConstraintError,
)
from src.core.exceptions.service_exceptions import ServiceError
from src.core.models.project import Project
from src.data.repository.project_repository import ProjectRepository


class ProjectService:
    """Phase-2 project service that applies business rules before repository access."""

    def __init__(self, repository: ProjectRepository):
        self._repository = repository

    def _validate_name(self, name: str) -> None:
        if not name or len(name.strip()) < 3:
            raise ServiceError("Project name must be at least 3 characters long.")

    def _validate_description(self, description: Optional[str]) -> None:
        if description is not None:
            text = description.strip()
            if len(text) < 10:
                raise ServiceError("Project description must be at least 10 characters when provided.")

    def _enforce_capacity(self) -> None:
        current_count = len(self._repository.list_all())
        if current_count >= Config.MAX_NUMBER_OF_PROJECT:
            raise ServiceError("Maximum number of projects reached.")

    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        self._validate_name(name)
        self._validate_description(description)
        self._enforce_capacity()

        try:
            return self._repository.create(name=name, description=description)
        except UniqueConstraintError as exc:
            raise ServiceError(str(exc)) from exc

    def list_projects(self) -> List[Project]:
        return self._repository.list_all()

    def get_project(self, project_id: int) -> Project:
        try:
            return self._repository.get_by_id(project_id)
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc

    def replace_project(
        self,
        project_id: int,
        name: Optional[str],
        description: Optional[str],
    ) -> Project:
        if name is None:
            raise ServiceError("Project name is required.")

        self._validate_name(name)
        self._validate_description(description)

        try:
            return self._repository.update(project_id, name, description)
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc
        except UniqueConstraintError as exc:
            raise ServiceError(str(exc)) from exc

    def update_project(
        self,
        project_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Project:
        if name is None and description is None:
            raise ServiceError("No valid fields provided for update.")

        if name is not None:
            self._validate_name(name)
        if description is not None:
            self._validate_description(description)

        try:
            return self._repository.update(project_id, name, description)
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc
        except UniqueConstraintError as exc:
            raise ServiceError(str(exc)) from exc

    def delete_project(self, project_id: int) -> None:
        try:
            self._repository.delete(project_id)
        except EntityNotFoundError as exc:
            raise ServiceError(str(exc)) from exc
