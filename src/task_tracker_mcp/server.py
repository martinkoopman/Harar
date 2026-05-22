import os
from dataclasses import asdict
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .storage import TaskStore

DEFAULT_PATH = Path.home() / ".task-tracker" / "tasks.json"
STORE_PATH = Path(os.environ.get("TASK_TRACKER_PATH", DEFAULT_PATH))

mcp = FastMCP("task-tracker")
store = TaskStore(STORE_PATH)


@mcp.tool()
def add_task(title: str, notes: str = "") -> dict:
    """Create a new task. Returns the created task."""
    return asdict(store.add(title=title, notes=notes))


@mcp.tool()
def list_tasks(status: str = "open") -> list[dict]:
    """List tasks. status is one of: open (default), done, all."""
    return [asdict(t) for t in store.list(status=status)]


@mcp.tool()
def complete_task(task_id: int) -> dict:
    """Mark a task as done."""
    return asdict(store.complete(task_id, done=True))


@mcp.tool()
def reopen_task(task_id: int) -> dict:
    """Mark a previously completed task as open again."""
    return asdict(store.complete(task_id, done=False))


@mcp.tool()
def update_task(task_id: int, title: str | None = None, notes: str | None = None) -> dict:
    """Update a task's title and/or notes."""
    return asdict(store.update(task_id, title=title, notes=notes))


@mcp.tool()
def delete_task(task_id: int) -> dict:
    """Delete a task. Returns the deleted task."""
    return asdict(store.delete(task_id))


@mcp.tool()
def clear_completed() -> dict:
    """Remove all tasks marked done. Returns the number deleted."""
    return {"removed": store.clear_done()}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
