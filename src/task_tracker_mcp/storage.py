import json
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Task:
    id: int
    title: str
    notes: str = ""
    done: bool = False
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    completed_at: str | None = None


class TaskStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _load(self) -> tuple[list[Task], int]:
        if not self.path.exists():
            return [], 1
        raw = json.loads(self.path.read_text() or "{}")
        tasks = [Task(**t) for t in raw.get("tasks", [])]
        next_id = raw.get("next_id", max((t.id for t in tasks), default=0) + 1)
        return tasks, next_id

    def _save(self, tasks: list[Task], next_id: int) -> None:
        payload = {"next_id": next_id, "tasks": [asdict(t) for t in tasks]}
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2))
        os.replace(tmp, self.path)

    def add(self, title: str, notes: str = "") -> Task:
        with self._lock:
            tasks, next_id = self._load()
            task = Task(id=next_id, title=title, notes=notes)
            tasks.append(task)
            self._save(tasks, next_id + 1)
            return task

    def list(self, status: str = "open") -> list[Task]:
        tasks, _ = self._load()
        if status == "all":
            return tasks
        if status == "done":
            return [t for t in tasks if t.done]
        if status == "open":
            return [t for t in tasks if not t.done]
        raise ValueError(f"unknown status: {status!r} (expected open|done|all)")

    def get(self, task_id: int) -> Task:
        tasks, _ = self._load()
        for t in tasks:
            if t.id == task_id:
                return t
        raise KeyError(f"no task with id {task_id}")

    def update(self, task_id: int, *, title: str | None = None, notes: str | None = None) -> Task:
        with self._lock:
            tasks, next_id = self._load()
            task = _find(tasks, task_id)
            if title is not None:
                task.title = title
            if notes is not None:
                task.notes = notes
            task.updated_at = _now()
            self._save(tasks, next_id)
            return task

    def complete(self, task_id: int, done: bool = True) -> Task:
        with self._lock:
            tasks, next_id = self._load()
            task = _find(tasks, task_id)
            task.done = done
            task.completed_at = _now() if done else None
            task.updated_at = _now()
            self._save(tasks, next_id)
            return task

    def delete(self, task_id: int) -> Task:
        with self._lock:
            tasks, next_id = self._load()
            task = _find(tasks, task_id)
            tasks = [t for t in tasks if t.id != task_id]
            self._save(tasks, next_id)
            return task

    def clear_done(self) -> int:
        with self._lock:
            tasks, next_id = self._load()
            remaining = [t for t in tasks if not t.done]
            removed = len(tasks) - len(remaining)
            self._save(remaining, next_id)
            return removed


def _find(tasks: Iterable[Task], task_id: int) -> Task:
    for t in tasks:
        if t.id == task_id:
            return t
    raise KeyError(f"no task with id {task_id}")
