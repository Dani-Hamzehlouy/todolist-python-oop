# src/cli/cli_app.py (FULL UPDATE)

from src.core.services import ToDoService
from src.core.models import Project
from datetime import datetime  # Needed to parse dates from user input
from typing import Optional


class CLIApp:
    """
    The Interface Layer (CLI).
    Handles user input, output, and error display. Communicates only with the Service Layer.
    """

    def __init__(self, service: ToDoService):
        self._service = service
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
        print("--- ToDoList CLI (In-Memory Phase 1) ---")
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

    # --- Project Methods (Full Implementation) ---

    def add_project(self, args: str):
        # ... (implementation remains the same)
        if not args:
            print("Usage: add-project TITLE;DESCRIPTION")
            return

        parts = [p.strip() for p in args.split(';', maxsplit=1)]
        title = parts[0]
        description = parts[1] if len(parts) > 1 else None

        try:
            project = self._service.create_project(title, description)
            print(f"SUCCESS: Project '{project.title}' created with ID: {project.id}")
        except (ValueError, OverflowError) as e:
            print(f"[ERROR] Could not create project: {e}")

    def list_projects(self, *args):
        projects = self._service.list_projects()

        if not projects:
            print("No projects exist.")
            return

        print("\n--- Projects List (Sorted by Creation Time) ---")
        for project in projects:
            desc = project.description if project.description else "No description"
            print(f"  [ID: {project.id}] | Name: {project.title} | Desc: {desc}")

    def edit_project(self, args: str):
        """Implements US (2): Edit Project."""
        parts = [p.strip() for p in args.split(';', maxsplit=2)]
        if len(parts) < 2:
            print("Usage: edit-project PROJECT_ID;NEW_TITLE;NEW_DESCRIPTION (optional)")
            return

        project_id, new_title = parts[0], parts[1]
        new_description = parts[2] if len(parts) == 3 else None

        try:
            project = self._service.update_project(project_id, new_title, new_description)
            print(f"SUCCESS: Project ID {project_id} updated to '{project.title}'")
        except ValueError as e:
            print(f"[ERROR] Could not update project: {e}")

    def delete_project(self, args: str):
        """Implements US (3): Delete Project (Cascade Delete)."""
        project_id = args.strip()
        if not project_id:
            print("Usage: delete-project PROJECT_ID")
            return

        try:
            if self._service.delete_project(project_id):
                print(f"SUCCESS: Project ID {project_id} deleted (and all associated tasks).")
            else:
                print(f"[ERROR] Project with ID '{project_id}' not found.")
        except Exception as e:
            print(f"[ERROR] Could not delete project: {e}")

    # --- Task Methods (Full Implementation) ---

    def add_task(self, args: str):
        """Implements US (4): Add Task to Project."""
        parts = [p.strip() for p in args.split(';', maxsplit=3)]
        if len(parts) < 2:
            print("Usage: add-task PROJECT_ID;TITLE;DESCRIPTION (optional);DEADLINE (YYYY-MM-DD) (optional)")
            return

        project_id, title = parts[0], parts[1]
        description = parts[2] if len(parts) > 2 else None
        deadline_str = parts[3] if len(parts) > 3 else None
        deadline: Optional[datetime] = None

        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                print("[ERROR] Invalid date format. Use YYYY-MM-DD.")
                return

        try:
            task = self._service.add_task_to_project(project_id, title, description, deadline)
            print(
                f"SUCCESS: Task '{task.title}' added to Project ID {project_id[:8]}... with Task ID: {task.id}")
        except (ValueError, OverflowError) as e:
            print(f"[ERROR] Could not add task: {e}")

    def list_tasks(self, args: str):
        """Implements US (9): List Tasks for a Project."""
        project_id = args.strip()
        if not project_id:
            print("Usage: list-tasks PROJECT_ID")
            return

        try:
            tasks = self._service.list_tasks_by_project(project_id)
            if not tasks:
                print(f"Project ID {project_id} found, but has no tasks.")
                return

            print(f"\n--- Tasks for Project ID {project_id[:8]} ---")
            for task in tasks:
                deadline_str = task.deadline.strftime("%Y-%m-%d") if task.deadline else "N/A"
                print(
                    f"  [ID: {task.id}] | Status: {task.status.upper():<5} | Deadline: {deadline_str:<10} | Title: {task.title}")
                if task.description:
                    print(f"    Desc: {task.description}")
        except ValueError as e:
            print(f"[ERROR] Could not list tasks: {e}")

    def edit_task(self, args: str):
        """Implements US (5): Edit Task."""
        parts = [p.strip() for p in args.split(';', maxsplit=3)]
        if len(parts) < 2:
            print("Usage: edit-task TASK_ID;NEW_TITLE;NEW_DESC (optional);NEW_DEADLINE (YYYY-MM-DD) (optional)")
            return

        task_id, new_title = parts[0], parts[1]
        new_description = parts[2] if len(parts) > 2 else None
        new_deadline_str = parts[3] if len(parts) > 3 else None
        new_deadline: Optional[datetime] = None

        if new_deadline_str:
            try:
                new_deadline = datetime.strptime(new_deadline_str, "%Y-%m-%d")
            except ValueError:
                print("[ERROR] Invalid date format for deadline. Use YYYY-MM-DD.")
                return

        try:
            task = self._service.update_task(task_id, new_title, new_description, new_deadline)
            print(f"SUCCESS: Task ID {task_id} updated to '{task.title}'")
        except ValueError as e:
            print(f"[ERROR] Could not update task: {e}")

    def delete_task(self, args: str):
        """Implements US (6): Delete Task."""
        task_id = args.strip()
        if not task_id:
            print("Usage: delete-task TASK_ID")
            return

        try:
            if self._service.delete_task(task_id):
                print(f"SUCCESS: Task ID {task_id} deleted.")
            else:
                print(f"[ERROR] Task with ID '{task_id}' not found.")
        except Exception as e:
            print(f"[ERROR] Could not delete task: {e}")

    def change_status(self, args: str):
        """Implements US (7): Change Task Status."""
        parts = [p.strip() for p in args.split(';', maxsplit=1)]
        if len(parts) != 2:
            print("Usage: change-status TASK_ID;NEW_STATUS (todo|doing|done)")
            return

        task_id, new_status = parts[0], parts[1].lower()

        try:
            task = self._service.change_task_status(task_id, new_status)
            print(f"SUCCESS: Task '{task.title}' status changed to '{task.status.upper()}'")
        except ValueError as e:
            print(f"[ERROR] Could not change status: {e}")