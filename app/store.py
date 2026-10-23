import itertools
import threading
from datetime import UTC, datetime
from typing import Any

from app.models import Task, TaskCreate, TaskStatus


class TaskStore:
    """In-memory, thread-safe task storage. Swapped for Postgres in a later phase."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._ids = itertools.count(1)
        self._lock = threading.Lock()

    def create(self, data: TaskCreate) -> Task:
        now = datetime.now(UTC)
        with self._lock:
            task = Task(id=next(self._ids), created_at=now, updated_at=now, **data.model_dump())
            self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def list(
        self,
        status: TaskStatus | None = None,
        query: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        with self._lock:
            tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        if query:
            tasks = [t for t in tasks if query.lower() in t.title.lower()]
        return tasks[offset : offset + limit], len(tasks)

    def update(self, task_id: int, changes: dict[str, Any]) -> Task | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            updated = task.model_copy(update={**changes, "updated_at": datetime.now(UTC)})
            self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None
