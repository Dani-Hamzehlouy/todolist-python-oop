"""FastAPI application entrypoint for Phase 3."""

from fastapi import FastAPI

app = FastAPI(title="ToDoList API", version="0.1.0")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint to verify the API is running."""
    return {"status": "ok"}

