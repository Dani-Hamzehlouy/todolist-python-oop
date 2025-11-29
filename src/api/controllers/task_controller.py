"""FastAPI controller for task resources."""

from __future__ import annotations

from typing import Generator, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.api.schemas.common import ApiResponse, ErrorResponse
from src.api.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.core.exceptions.service_exceptions import ServiceError
from src.core.services.project_service import ProjectService
from src.core.services.task_service import TaskService
from src.data.repository.project_repository import SqlAlchemyProjectRepository
from src.data.repository.task_repository import SqlAlchemyTaskRepository
from src.db.session import SessionLocal

router = APIRouter(prefix="/api", tags=["Task Management"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    project_repo = SqlAlchemyProjectRepository(db)
    task_repo = SqlAlchemyTaskRepository(db)
    return TaskService(task_repo, project_repo)


def _raise_http_error(exc: ServiceError) -> None:
    message = str(exc)
    lowered = message.lower()
    if "not found" in lowered:
        status_code = status.HTTP_404_NOT_FOUND
    elif "exists" in lowered or "maximum" in lowered or "capacity" in lowered:
        status_code = status.HTTP_409_CONFLICT
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    error = ErrorResponse(status="error", message=message)
    raise HTTPException(status_code=status_code, detail=error.model_dump())


@router.post(
    "/projects/{project_id}/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse,
    summary="Create a task",
    description="Add a new task under the specified project. "
    "Task limits, project existence, and field validations are enforced.",
)
def create_task(
    project_id: int,
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    try:
        task = service.create_task(
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            deadline=payload.deadline,
        )
        data = TaskResponse.model_validate(task, from_attributes=True)
        return ApiResponse(status="success", data=data, message="Task created.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.get(
    "/projects/{project_id}/tasks",
    response_model=ApiResponse,
    summary="List tasks for a project",
    description="Retrieve every task that belongs to the given project identifier.",
)
def list_tasks(
    project_id: int,
    service: TaskService = Depends(get_task_service),
) -> List[TaskResponse]:
    try:
        tasks = service.list_tasks(project_id)
        data = [TaskResponse.model_validate(task, from_attributes=True) for task in tasks]
        return ApiResponse(status="success", data=data, message="Tasks retrieved.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.get(
    "/tasks/{task_id}",
    response_model=ApiResponse,
    summary="Retrieve a task",
    description="Return a single task by ID. Responds with 404 if the task does not exist.",
)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    try:
        task = service.get_task(task_id)
        data = TaskResponse.model_validate(task, from_attributes=True)
        return ApiResponse(status="success", data=data, message="Task retrieved.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.put(
    "/tasks/{task_id}",
    response_model=ApiResponse,
    summary="Replace a task",
    description="Fully replace a task's fields. Requires title, description, status, and deadline values.",
)
def replace_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> ApiResponse:
    if not all([payload.title, payload.description, payload.status, payload.deadline]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                status="error",
                message="title, description, status, and deadline are required for replacement.",
            ).model_dump(),
        )

    try:
        task = service.replace_task(
            task_id,
            title=payload.title,
            description=payload.description,
            status=payload.status.value if payload.status else None,
            deadline=payload.deadline,
        )
        data = TaskResponse.model_validate(task, from_attributes=True)
        return ApiResponse(status="success", data=data, message="Task replaced.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.patch(
    "/tasks/{task_id}",
    response_model=ApiResponse,
    summary="Update a task",
    description="Partially update task fields such as title, description, status, or deadline.",
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    if not any([payload.title, payload.description, payload.status, payload.deadline]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided to update.",
        )

    try:
        task = service.update_task(
            task_id,
            title=payload.title,
            description=payload.description,
            status=payload.status.value if payload.status else None,
            deadline=payload.deadline,
        )
        data = TaskResponse.model_validate(task, from_attributes=True)
        return ApiResponse(status="success", data=data, message="Task updated.")
    except ServiceError as exc:
        _raise_http_error(exc)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Remove a task permanently. Responds with 204 even if no body is returned.",
)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> Response:
    try:
        service.delete_task(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ServiceError as exc:
        _raise_http_error(exc)
