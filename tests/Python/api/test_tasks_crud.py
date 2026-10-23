from datetime import datetime

import pytest

from framework.assertions import assert_status
from framework.factories import task_payload


@pytest.mark.smoke
def test_create_task_returns_201_and_echoes_fields(tasks_api):
    payload = task_payload(priority=5, status="in_progress")

    response = tasks_api.create(payload)
    body = response.json()
    tasks_api.delete(body["id"])

    assert_status(response, 201)
    assert {key: body[key] for key in payload} == payload
    assert isinstance(body["id"], int)
    assert body["created_at"] == body["updated_at"]


def test_create_applies_defaults(tasks_api):
    response = tasks_api.create({"title": "only a title"})
    body = response.json()
    tasks_api.delete(body["id"])

    assert body["status"] == "todo"
    assert body["priority"] == 3
    assert body["description"] is None


def test_create_strips_title_whitespace(create_task):
    assert create_task(title="  padded  ")["title"] == "padded"


@pytest.mark.smoke
def test_get_task_by_id(create_task, tasks_api):
    task = create_task()

    response = tasks_api.get(task["id"])

    assert_status(response, 200)
    assert response.json() == task


@pytest.mark.parametrize(
    "changes",
    [
        {"title": "renamed"},
        {"status": "done"},
        {"priority": 1},
        {"description": None},
        {"status": "in_progress", "priority": 4},
    ],
    ids=["title", "status", "priority", "clear-description", "multiple"],
)
def test_patch_updates_only_given_fields(create_task, tasks_api, changes):
    task = create_task()

    response = tasks_api.update(task["id"], changes)

    assert_status(response, 200)
    updated = response.json()
    assert updated == {**task, **changes, "updated_at": updated["updated_at"]}
    assert datetime.fromisoformat(updated["updated_at"]) >= datetime.fromisoformat(
        task["updated_at"]
    )
    # The change must be persisted, not just echoed back.
    assert tasks_api.get(task["id"]).json() == updated


def test_delete_task_removes_it(create_task, tasks_api):
    task = create_task()

    assert_status(tasks_api.delete(task["id"]), 204)
    assert_status(tasks_api.get(task["id"]), 404)


def test_delete_twice_returns_404(create_task, tasks_api):
    task = create_task()
    tasks_api.delete(task["id"])

    assert_status(tasks_api.delete(task["id"]), 404)
