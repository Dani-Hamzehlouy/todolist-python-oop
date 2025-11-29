"""FastAPI application entrypoint for Phase 3."""

from fastapi import FastAPI

from src.api.controllers.project_controller import router as project_router

app = FastAPI(title="ToDoList API", version="0.1.0")
app.include_router(project_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint to verify the API is running."""
    return {"status": "ok"}
