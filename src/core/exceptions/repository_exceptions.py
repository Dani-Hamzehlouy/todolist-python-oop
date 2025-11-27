from src.core.exceptions.base import AppError


class RepositoryError(AppError):
    """Base error for repository-level failures."""


class EntityNotFoundError(RepositoryError):
    """Raised when a requested entity cannot be located."""


class UniqueConstraintError(RepositoryError):
    """Raised when a uniqueness constraint is violated."""
