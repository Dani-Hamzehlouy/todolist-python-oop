from src.core.exceptions.base import AppError


class ServiceError(AppError):
    """Base error for service-layer violations."""


class InvalidTaskOperationError(ServiceError):
    """Raised when an illegal operation is attempted on a task."""
