"""FastAPI controller for project resources."""

from __future__ import annotations

from typing import Generator, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.api.schemas.common import ApiResponse, ErrorResponse
from src.api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from src.core.exceptions.service_exceptions import ServiceError
from src.core.services.project_service import ProjectService
from src.data.repository.project_repository import SqlAlchemyProjectRepository
from src.db.session import SessionLocal

router = APIRouter(prefix="/api/projects", tags=["Project Management"])


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
    error = ErrorResponse(status="error", message=message)
    raise HTTPException(status_code=status_code, detail=error.model_dump())


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse,
    summary="Create a project",
    description="Create a new project by providing its name and optional description. "
    "The request enforces business rules such as name length and total project capacity.",
)
def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    try:
        project = service.create_project(name=payload.name, description=payload.description)
        data = ProjectResponse.model_validate(project, from_attributes=True)
        return ApiResponse(status="success", data=data, message="Project created.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.get(
    "",
    response_model=ApiResponse,
    summary="List all projects",
    description="Return all projects stored in the system, ordered by creation time.",
)
def list_projects(
    service: ProjectService = Depends(get_project_service),
) -> List[ProjectResponse]:
    projects = service.list_projects()
    data = [ProjectResponse.model_validate(project, from_attributes=True) for project in projects]
    return ApiResponse(status="success", data=data, message="Projects retrieved.")


@router.get(
    "/{project_id}",
    response_model=ApiResponse,
    summary="Retrieve a project",
    description="Fetch a single project by its identifier. Returns 404 if the project does not exist.",
)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    try:
        project = service.get_project(project_id)
        data = ProjectResponse.model_validate(project, from_attributes=True)
        return ApiResponse(status="success", data=data, message="Project retrieved.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.put(
    "/{project_id}",
    response_model=ApiResponse,
    summary="Replace a project",
    description="Fully replace an existing project with the provided data. "
    "Validates name and description according to business rules.",
)
def replace_project(
    project_id: int,
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    try:
        project = service.replace_project(project_id, name=payload.name, description=payload.description)
        data = ProjectResponse.model_validate(project, from_attributes=True)
        return ApiResponse(status="success", data=data, message="Project replaced.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.patch(
    "/{project_id}",
    response_model=ApiResponse,
    summary="Update project fields",
    description="Partially update a project. Allows changing name, description, or both.",
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    if payload.name is None and payload.description is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(status="error", message="At least one field must be provided to update.").model_dump(),
        )

    try:
        project = service.update_project(project_id, name=payload.name, description=payload.description)
        data = ProjectResponse.model_validate(project, from_attributes=True)
        return ApiResponse(status="success", data=data, message="Project updated.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description="Remove a project and all associated tasks. Responds with 204 on success.",
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
