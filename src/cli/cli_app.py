# src/cli/cli_app.py

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
            "add-project": self.add_project,
            "list-projects": self.list_projects,
            # Placeholder for other commands (add-task, edit-project, etc.)
            "help": self.show_help,
        }

    def run(self):
        """Starts the main application loop."""
        print("--- ToDoList CLI (In-Memory Phase 1) ---")
        self.show_help()
        while self.running:
            try:
                # Get command from user
                user_input = input("\nEnter command (or 'help'): ").strip()
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if command in self.commands:
                    self.commands[command](args)
                elif command:
                    print(f"Error: Unknown command '{command}'. Type 'help' for available commands.")

            except Exception as e:
                # Non-Functional Requirement: User-friendly error messages[cite: 43].
                print(f"\n[ERROR] Operation failed: {e}")

    def stop(self, *args):
        """Stops the application."""
        print("Exiting ToDoList. All in-memory data will be lost.")
        self.running = False

    def show_help(self, *args):
        """Displays available commands."""
        print("\nAvailable Commands:")
        print("  list-projects        : Show all projects.")
        print("  add-project TITLE DESCRIPTION: Create a new project.")
        print("  exit                 : Close the application (data is lost).")
        print("  help                 : Show this message.")

    # --- Project Methods (Implementing User Stories) ---

    def add_project(self, args: str):
        """
        Implements US (1): Create Project.
        Example args format: "My Project Title;A detailed description"
        """
        if not args:
            print("Usage: add-project TITLE;DESCRIPTION")
            return

        parts = [p.strip() for p in args.split(';', maxsplit=1)]
        title = parts[0]
        description = parts[1] if len(parts) > 1 else None

        try:
            # Service layer enforces all constraints (word limits, uniqueness, capacity)
            project = self._service.create_project(title, description)
            print(f"SUCCESS: Project '{project.title}' created with ID: {project.id}")
        except (ValueError, OverflowError) as e:
            # Display appropriate error messages[cite: 43].
            print(f"[ERROR] Could not create project: {e}")

    def list_projects(self, *args):
        """
        Implements US (8): Display List of Projects.
        """
        projects = self._service.list_projects()

        if not projects:
            # Acceptance Criteria: Display appropriate message if no projects exist[cite: 114].
            print("No projects exist.")
            return

        print("\n--- Projects List (Sorted by Creation Time) ---")

        # Acceptance Criteria: Show ID, Name, and Description[cite: 113].
        for project in projects:
            desc = project.description if project.description else "No description"
            print(f"  [ID: {project.id[:8]}...] | Name: {project.title} | Desc: {desc}")