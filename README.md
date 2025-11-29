# ToDoList - Python OOP (In-Memory)

## 🎯 Project Overview

This project is the initial **Phase 1** of a multi-phase development effort to build a robust ToDo List application using **Python's Object-Oriented Programming (OOP)** principles.

This phase is a **Command Line Interface (CLI)** application that uses **In-Memory** storage (data is lost upon exit), focusing entirely on establishing a clean, modular, and extensible architecture.

---

### Key Architectural Principles

The application is strictly designed using a **Layered Architecture** to ensure **Separation of Concerns (SoC)**, making future phases (adding persistency and switching to a Web API) simpler.

| Layer | Responsibility | Directory | Key Components |
| :--- | :--- | :--- | :--- |
| **Interface** | User Input/Output (I/O) | `src/cli/` & `main.py` | `CLIApp` |
| **Business Logic** | Core rules, orchestration, flow control. | `src/core/` | `ToDoService` |
| **Data Access** | Storage and retrieval mechanism (In-Memory in Phase 1). | `src/data/` | `ProjectRepository` |
| **Models** | Data structure definition and validation (e.g., word limits). | `src/core/` | `Project`, `Task` |

---

## 🛠️ Setup and Installation (Mandatory Tools)

This project requires **Poetry** for dependency management, as mandated by the project requirements.

### 1. Requirements

* Python 3.8+
* [Poetry](https://python-poetry.org/docs/#installation) (Installed globally)
* Git / GitHub

### 2. Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Dani-Hamzehlouy/todolist-python-oop.git
    cd todo-list-python-oop
    ```

2.  **Install Dependencies with Poetry:**
    ```bash
    # Creates the virtual environment and installs 'python-dotenv'
    poetry install
    ```

3.  **Activate the Environment (Optional but Recommended):**
    ```bash
    poetry shell
    ```
    *If not using `poetry shell`, you must prefix all runs with `poetry run`.*

4.  **Create Configuration File:**
    Copy the example configuration to your active environment file:
    ```bash
    cp .env.example .env
    ```

---

## ⚙️ Configuration

The application reads essential constraints from the **`.env`** file located in the root directory.

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `MAX_NUMBER_OF_PROJECT` | `5` | Limits the total number of projects. |
| `MAX_NUMBER_OF_TASK` | `20` | Limits the total tasks *per project*. |



---

## 🚀 Running the Application

Start the CLI application using the Poetry runner:

```bash
poetry run python main.py
```

---

## Phase 3 – Web API

The new FastAPI service will eventually replace the CLI. Start it locally with Poetry:

```bash
poetry run uvicorn src.api.main:app --reload
```

Then verify it responds:

```bash
curl http://127.0.0.1:8000/health
```
