"""FastAPI controller for task resources."""

from __future__ import annotations

from typing import Generator, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.api.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.core.exceptions.service_exceptions import ServiceError
from src.core.services.project_service import ProjectService
from src.core.services.task_service import TaskService
from src.data.repository.project_repository import SqlAlchemyProjectRepository
from src.data.repository.task_repository import SqlAlchemyTaskRepository
from src.db.session import SessionLocal

router = APIRouter(prefix="/api", tags=["tasks"])


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
    raise HTTPException(status_code=status_code, detail=message)


@router.post(
    "/projects/{project_id}/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse,
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
        return TaskResponse.model_validate(task, from_attributes=True)
    except ServiceError as exc:
        _raise_http_error(exc)


@router.get(
    "/projects/{project_id}/tasks",
    response_model=List[TaskResponse],
)
def list_tasks(
    project_id: int,
    service: TaskService = Depends(get_task_service),
) -> List[TaskResponse]:
    try:
        tasks = service.list_tasks(project_id)
        return [TaskResponse.model_validate(task, from_attributes=True) for task in tasks]
    except ServiceError as exc:
        _raise_http_error(exc)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    try:
        task = service.get_task(task_id)
        return TaskResponse.model_validate(task, from_attributes=True)
    except ServiceError as exc:
        _raise_http_error(exc)


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
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
        return TaskResponse.model_validate(task, from_attributes=True)
    except ServiceError as exc:
        _raise_http_error(exc)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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
