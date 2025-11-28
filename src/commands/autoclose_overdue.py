from datetime import datetime

from src.core.services.project_service import ProjectService
from src.core.services.task_service import TaskService
from src.data.repository.project_repository import SqlAlchemyProjectRepository
from src.data.repository.task_repository import SqlAlchemyTaskRepository
from src.db.session import SessionLocal


def main() -> None:
    session = SessionLocal()
    project_repo = SqlAlchemyProjectRepository(session)
    task_repo = SqlAlchemyTaskRepository(session)
    project_service = ProjectService(project_repo)
    task_service = TaskService(project_repo, task_repo)

    try:
        now = datetime.utcnow()
        overdue_tasks = task_service.find_overdue_open_tasks(now)
        updated_count = 0

        for task in overdue_tasks:
            task_service.update_task(task.id, status="done", at_closed=now)
            updated_count += 1

        print(f"Overdue tasks found: {len(overdue_tasks)}")
        print(f"Tasks updated: {updated_count}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
