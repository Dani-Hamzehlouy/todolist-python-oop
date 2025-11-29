"""FastAPI controller for project resources."""

from __future__ import annotations

from typing import Generator, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from src.core.exceptions.service_exceptions import ServiceError
from src.core.services.project_service import ProjectService
from src.data.repository.project_repository import SqlAlchemyProjectRepository
from src.db.session import SessionLocal

router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    repository = SqlAlchemyProjectRepository(db)
    return ProjectService(repository)


def _raise_http_error(exc: ServiceError) -> None:
    message = str(exc)
    lowered = message.lower()
    if "not found" in lowered:
        status_code = status.HTTP_404_NOT_FOUND
    elif "exists" in lowered:
        status_code = status.HTTP_409_CONFLICT
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    raise HTTPException(status_code=status_code, detail=message)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectResponse,
)
def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    try:
        project = service.create_project(name=payload.name, description=payload.description)
        return ProjectResponse.model_validate(project, from_attributes=True)
    except ServiceError as exc:
        _raise_http_error(exc)


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    service: ProjectService = Depends(get_project_service),
) -> List[ProjectResponse]:
    projects = service.list_projects()
    return [ProjectResponse.model_validate(project, from_attributes=True) for project in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    try:
        project = service.get_project(project_id)
        return ProjectResponse.model_validate(project, from_attributes=True)
    except ServiceError as exc:
        _raise_http_error(exc)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
)
def replace_project(
    project_id: int,
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    try:
        project = service.update_project(project_id, name=payload.name, description=payload.description)
        return ProjectResponse.model_validate(project, from_attributes=True)
    except ServiceError as exc:
        _raise_http_error(exc)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    if payload.name is None and payload.description is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided to update.",
        )

    try:
        project = service.update_project(project_id, name=payload.name, description=payload.description)
        return ProjectResponse.model_validate(project, from_attributes=True)
    except ServiceError as exc:
        _raise_http_error(exc)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> Response:
    try:
        service.delete_project(project_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ServiceError as exc:
        _raise_http_error(exc)
