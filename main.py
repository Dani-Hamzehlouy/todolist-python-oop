# main.py

from src.data.repository import ProjectRepository
from src.core.services import ToDoService
from src.cli.cli_app import CLIApp

if __name__ == "__main__":
    # 1. Initialize the Data Access Layer
    repo = ProjectRepository()

    # 2. Initialize the Business Logic Layer, injecting the repository
    service = ToDoService(repository=repo)

    # 3. Initialize the Interface Layer, injecting the service
    app = CLIApp(service=service)

    # 4. Run the application
    app.run()