import pytest

from framework.assertions import assert_status
from framework.contracts import ErrorContract, ValidationErrorContract, issue_locations
from framework.factories import task_payload

INVALID_CREATE_PAYLOADS = [
    pytest.param({"description": "no title"}, ("body", "title"), id="missing-title"),
    pytest.param(task_payload(title=""), ("body", "title"), id="empty-title"),
    pytest.param(task_payload(title="   "), ("body", "title"), id="blank-title"),
    pytest.param(task_payload(title="x" * 201), ("body", "title"), id="title-too-long"),
    pytest.param(task_payload(title=123), ("body", "title"), id="title-not-string"),
    pytest.param(
        task_payload(description="x" * 2001), ("body", "description"), id="description-too-long"
    ),
    pytest.param(task_payload(priority=0), ("body", "priority"), id="priority-below-min"),
    pytest.param(task_payload(priority=6), ("body", "priority"), id="priority-above-max"),
    pytest.param(task_payload(priority="high"), ("body", "priority"), id="priority-not-int"),
    pytest.param(task_payload(status="blocked"), ("body", "status"), id="unknown-status"),
    pytest.param(task_payload(owner="me"), ("body", "owner"), id="unknown-field"),
]


@pytest.mark.parametrize(("payload", "location"), INVALID_CREATE_PAYLOADS)
def test_create_rejects_invalid_payload(tasks_api, payload, location):
    response = tasks_api.create(payload)

    assert_status(response, 422)
    ValidationErrorContract.model_validate_json(response.text)
    assert location in issue_locations(response.json())


def test_create_rejects_non_json_body(api_client):
    response = api_client.post(
        "/tasks", data="title=x", headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert_status(response, 422)


@pytest.mark.parametrize(
    "changes",
    [{"title": None}, {"status": None}, {"priority": 10}, {"title": ""}, {"id": 99}],
    ids=["null-title", "null-status", "bad-priority", "empty-title", "readonly-id"],
)
def test_patch_rejects_invalid_changes(create_task, tasks_api, changes):
    task = create_task()

    assert_status(tasks_api.update(task["id"], changes), 422)
    assert tasks_api.get(task["id"]).json() == task


@pytest.mark.parametrize(
    "call",
    [
        lambda api: api.get(999_999_999),
        lambda api: api.update(999_999_999, {"title": "x"}),
        lambda api: api.delete(999_999_999),
    ],
    ids=["get", "patch", "delete"],
)
def test_unknown_task_returns_404(tasks_api, call):
    response = call(tasks_api)

    assert_status(response, 404)
    assert "not found" in ErrorContract.model_validate_json(response.text).detail


@pytest.mark.parametrize("task_id", ["abc", "1.5"])
def test_non_integer_id_returns_422(tasks_api, task_id):
    assert_status(tasks_api.get(task_id), 422)


@pytest.mark.parametrize(
    "params",
    [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"status": "blocked"}],
    ids=["limit-zero", "limit-too-big", "negative-offset", "unknown-status"],
)
def test_list_rejects_invalid_query_params(tasks_api, params):
    assert_status(tasks_api.list(**params), 422)
