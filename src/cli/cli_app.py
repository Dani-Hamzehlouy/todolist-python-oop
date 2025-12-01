"""Deprecated CLI interface retained temporarily for Phase 3 compatibility."""

# src/cli/cli_app.py (FULL UPDATE)

from datetime import datetime  # Needed to parse dates from user input
from typing import Optional

from src.core.exceptions.service_exceptions import InvalidTaskOperationError, ServiceError
from src.core.services.project_service import ProjectService
from src.core.services.task_service import TaskService
from src.data.repository.project_repository import SqlAlchemyProjectRepository
from src.data.repository.task_repository import SqlAlchemyTaskRepository
from src.db.session import SessionLocal

_warning_printed = False


def print_cli_deprecation_warning() -> None:
    """Emit the CLI deprecation warning once per process run."""
    global _warning_printed
    if not _warning_printed:
        print(
            "WARNING: The CLI interface is deprecated and will be removed in a future version. "
            "Please use the FastAPI Web API instead."
        )
        _warning_printed = True


class CLIApp:
    """
    The Interface Layer (CLI).
    Handles user input, output, and error display. Communicates only with the Service Layer.
    """

    def __init__(self, service=None):
        print_cli_deprecation_warning()
        self._service = service  # maintained for backward compatibility; no longer used
        self.running = True
        self.commands = {
            "exit": self.stop,
            "help": self.show_help,

            # Project Commands
            "add-project": self.add_project,
            "list-projects": self.list_projects,
            "edit-project": self.edit_project,  # US (2)
            "delete-project": self.delete_project,  # US (3)

            # Task Commands
            "add-task": self.add_task,  # US (4)
            "list-tasks": self.list_tasks,  # US (9)
            "edit-task": self.edit_task,  # US (5)
            "delete-task": self.delete_task,  # US (6)
            "change-status": self.change_status,  # US (7)
        }

    def run(self):
        """Starts the main application loop."""
        print("--- ToDoList CLI (Phase 2 — Database Mode) ---")
        self.show_help()
        while self.running:
            try:
                user_input = input("\nEnter command (or 'help'): ").strip()
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if command in self.commands:
                    self.commands[command](args)
                elif command:
                    print(f"Error: Unknown command '{command}'. Type 'help' for available commands.")

            except Exception as e:
                print(f"\n[ERROR] Operation failed: {e}")

    def stop(self, *args):
        """Stops the application."""
        print("Exiting ToDoList. All in-memory data will be lost.")
        self.running = False

    def show_help(self, *args):
        """Displays available commands."""
        print("\n--- ToDo List Commands ---")
        print("\nPROJECT MANAGEMENT:")
        print("  list-projects                             : Show all projects.")
        print("  add-project TITLE;DESCRIPTION             : Create a new project.")
        print("  edit-project ID;NEW_TITLE;NEW_DESC        : Update project title/description.")
        print("  delete-project ID                         : Delete project (cascades to tasks).")

        print("\nTASK MANAGEMENT:")
        print("  list-tasks PROJECT_ID                     : Show all tasks for a project.")
        print("  add-task PROJECT_ID;TITLE;DESCRIPTION;DEADLINE (YYYY-MM-DD) : Add a new task.")
        print("  edit-task TASK_ID;NEW_TITLE;NEW_DESC;NEW_DEADLINE         : Update a task.")
        print("  delete-task TASK_ID                       : Delete a task.")
        print("  change-status TASK_ID;STATUS (todo|doing|done) : Update task status.")

        print("\nSYSTEM:")
        print("  exit                 : Close the application (data is lost).")
        print("  help                 : Show this message.")

    # --- Helper Methods ---

    @staticmethod
    def _parse_int(value: str, entity_name: str) -> Optional[int]:
        try:
            return int(value)
        except ValueError:
            print(f"[ERROR] {entity_name} must be a numeric ID.")
            return None

    # --- Project Methods (Full Implementation) ---

    def add_project(self, args: str):
        # ... (implementation remains the same)
        if not args:
            print("Usage: add-project TITLE;DESCRIPTION")
            return

        parts = [p.strip() for p in args.split(';', maxsplit=1)]
        title = parts[0]
        description = parts[1] if len(parts) > 1 else None

        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            project = project_service.create_project(title, description)
            print(f"SUCCESS: Project '{project.name}' created with ID: {project.id}")
        except ServiceError as e:
            print(f"[ERROR] Could not create project: {e}")
        finally:
            session.close()

    def list_projects(self, *args):
        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            projects = project_service.list_projects()
        except ServiceError as e:
            print(f"[ERROR] Could not list projects: {e}")
            return
        finally:
            session.close()

        if not projects:
            print("No projects exist.")
            return

        print("\n--- Projects List (Sorted by Creation Time) ---")
        for project in projects:
            desc = project.description if project.description else "No description"
            print(f"  [ID: {project.id}] | Name: {project.name} | Desc: {desc}")

    def edit_project(self, args: str):
        """Implements US (2): Edit Project."""
        parts = [p.strip() for p in args.split(';', maxsplit=2)]
        if len(parts) < 2:
            print("Usage: edit-project PROJECT_ID;NEW_TITLE;NEW_DESCRIPTION (optional)")
            return

        project_id_value = self._parse_int(parts[0], "Project ID")
        if project_id_value is None:
            return

        project_id, new_title = project_id_value, parts[1]
        new_description = parts[2] if len(parts) == 3 else None

        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            project = project_service.update_project(project_id, new_title, new_description)
            print(f"SUCCESS: Project ID {project_id} updated to '{project.name}'")
        except ServiceError as e:
            print(f"[ERROR] Could not update project: {e}")
        finally:
            session.close()

    def delete_project(self, args: str):
        """Implements US (3): Delete Project (Cascade Delete)."""
        project_id_raw = args.strip()
        if not project_id_raw:
            print("Usage: delete-project PROJECT_ID")
            return

        project_id = self._parse_int(project_id_raw, "Project ID")
        if project_id is None:
            return

        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            project_service.delete_project(project_id)
            print(f"SUCCESS: Project ID {project_id} deleted (and all associated tasks).")
        except ServiceError as e:
            print(f"[ERROR] Could not delete project: {e}")
        finally:
            session.close()

    # --- Task Methods (Full Implementation) ---

    def add_task(self, args: str):
        """Implements US (4): Add Task to Project."""
        parts = [p.strip() for p in args.split(';', maxsplit=3)]
        if len(parts) < 2:
            print("Usage: add-task PROJECT_ID;TITLE;DESCRIPTION (optional);DEADLINE (YYYY-MM-DD) (optional)")
            return

        project_id = self._parse_int(parts[0], "Project ID")
        if project_id is None:
            return

        title = parts[1]
        description = parts[2] if len(parts) > 2 else None
        deadline_str = parts[3] if len(parts) > 3 else None
        deadline: Optional[datetime] = None

        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                print("[ERROR] Invalid date format. Use YYYY-MM-DD.")
                return

        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            task = task_service.create_task(project_id, title, description, deadline)
            project_id_str = str(project_id)
            print(
                f"SUCCESS: Task '{task.title}' added to Project ID {project_id_str[:8]}... with Task ID: {task.id}")
        except (ServiceError, InvalidTaskOperationError) as e:
            print(f"[ERROR] Could not add task: {e}")
        finally:
            session.close()

    def list_tasks(self, args: str):
        """Implements US (9): List Tasks for a Project."""
        project_id_raw = args.strip()
        if not project_id_raw:
            print("Usage: list-tasks PROJECT_ID")
            return

        project_id = self._parse_int(project_id_raw, "Project ID")
        if project_id is None:
            return

        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            tasks = task_service.list_tasks(project_id)
        except ServiceError as e:
            print(f"[ERROR] Could not list tasks: {e}")
            return
        finally:
            session.close()

        if not tasks:
            print(f"Project ID {project_id} found, but has no tasks.")
            return

        project_id_str = str(project_id)
        print(f"\n--- Tasks for Project ID {project_id_str[:8]} ---")
        for task in tasks:
            deadline_str = task.deadline.strftime("%Y-%m-%d") if task.deadline else "N/A"
            print(
                f"  [ID: {task.id}] | Status: {task.status.upper():<5} | Deadline: {deadline_str:<10} | Title: {task.title}")
            if task.description:
                print(f"    Desc: {task.description}")

    def edit_task(self, args: str):
        """Implements US (5): Edit Task."""
        parts = [p.strip() for p in args.split(';', maxsplit=3)]
        if len(parts) < 2:
            print("Usage: edit-task TASK_ID;NEW_TITLE;NEW_DESC (optional);NEW_DEADLINE (YYYY-MM-DD) (optional)")
            return

        task_id = self._parse_int(parts[0], "Task ID")
        if task_id is None:
            return

        new_title = parts[1]
        new_description = parts[2] if len(parts) > 2 else None
        new_deadline_str = parts[3] if len(parts) > 3 else None
        new_deadline: Optional[datetime] = None

        if new_deadline_str:
            try:
                new_deadline = datetime.strptime(new_deadline_str, "%Y-%m-%d")
            except ValueError:
                print("[ERROR] Invalid date format for deadline. Use YYYY-MM-DD.")
                return

        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            task = task_service.update_task(
                task_id,
                title=new_title,
                description=new_description,
                deadline=new_deadline,
            )
            print(f"SUCCESS: Task ID {task_id} updated to '{task.title}'")
        except (ServiceError, InvalidTaskOperationError) as e:
            print(f"[ERROR] Could not update task: {e}")
        finally:
            session.close()

    def delete_task(self, args: str):
        """Implements US (6): Delete Task."""
        task_id_raw = args.strip()
        if not task_id_raw:
            print("Usage: delete-task TASK_ID")
            return

        task_id = self._parse_int(task_id_raw, "Task ID")
        if task_id is None:
            return

        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            task_service.delete_task(task_id)
            print(f"SUCCESS: Task ID {task_id} deleted.")
        except ServiceError as e:
            print(f"[ERROR] Could not delete task: {e}")
        finally:
            session.close()

    def change_status(self, args: str):
        """Implements US (7): Change Task Status."""
        parts = [p.strip() for p in args.split(';', maxsplit=1)]
        if len(parts) != 2:
            print("Usage: change-status TASK_ID;NEW_STATUS (todo|doing|done)")
            return

        task_id = self._parse_int(parts[0], "Task ID")
        if task_id is None:
            return

        new_status = parts[1].lower()

        session = SessionLocal()
        project_repo = SqlAlchemyProjectRepository(session)
        task_repo = SqlAlchemyTaskRepository(session)
        project_service = ProjectService(project_repo)
        task_service = TaskService(task_repo, project_repo)

        try:
            task = task_service.update_task(task_id, status=new_status)
            print(f"SUCCESS: Task '{task.title}' status changed to '{task.status.upper()}'")
        except (ServiceError, InvalidTaskOperationError) as e:
            print(f"[ERROR] Could not change status: {e}")
        finally:
            session.close()
