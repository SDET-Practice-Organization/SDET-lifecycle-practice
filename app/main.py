"""TaskApp: a small task-tracking API used as the system under test."""

import os
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query, Response, status

from app import bugs
from app.models import Task, TaskCreate, TaskList, TaskStatus, TaskUpdate
from app.store import TaskStore

VERSION = "0.1.0"
API_KEY = os.environ.get("TASKAPP_API_KEY", "dev-key")

app = FastAPI(title="TaskApp", version=VERSION)
store = TaskStore()


def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API key")


def get_task_or_404(task_id: int) -> Task:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task {task_id} not found")
    return task


router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_api_key)])


@app.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": VERSION}


@router.get("", response_model=TaskList)
def list_tasks(
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    q: Annotated[
        str | None, Query(max_length=200, description="Case-insensitive title search")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TaskList:
    effective_status = None if bugs.enabled("filter_ignored") else status_filter
    effective_offset = offset + 1 if bugs.enabled("pagination_off_by_one") else offset
    items, total = store.list(effective_status, q, limit, effective_offset)
    return TaskList(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, response: Response) -> Task:
    if bugs.enabled("create_returns_200"):
        response.status_code = status.HTTP_200_OK
    return store.create(payload)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    return get_task_or_404(task_id)


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    get_task_or_404(task_id)
    changes = payload.model_dump(exclude_unset=True)
    if bugs.enabled("patch_ignores_status"):
        changes.pop("status", None)
    return store.update(task_id, changes)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    get_task_or_404(task_id)
    if not bugs.enabled("delete_not_persisted"):
        store.delete(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


app.include_router(router)
