import pytest

from framework.assertions import assert_status
from framework.contracts import TaskContract, TaskListContract
from framework.factories import task_payload

pytestmark = pytest.mark.contract


def test_create_contract(tasks_api):
    response = tasks_api.create(task_payload())
    tasks_api.delete(response.json()["id"])

    assert response.headers["Content-Type"] == "application/json"
    TaskContract.model_validate_json(response.text)


def test_get_and_patch_contract(create_task, tasks_api):
    task = create_task()

    for response in (tasks_api.get(task["id"]), tasks_api.update(task["id"], {"priority": 2})):
        assert_status(response, 200)
        assert response.headers["Content-Type"] == "application/json"
        TaskContract.model_validate_json(response.text)


def test_list_contract(create_task, tasks_api):
    create_task()

    response = tasks_api.list(limit=5)

    assert_status(response, 200)
    TaskListContract.model_validate_json(response.text)


def test_delete_has_empty_body(create_task, tasks_api):
    response = tasks_api.delete(create_task()["id"])

    assert_status(response, 204)
    assert response.content == b""


def test_openapi_documents_all_operations(api_client):
    spec = api_client.get("/openapi.json").json()

    operations = {(path, method) for path, ops in spec["paths"].items() for method in ops}
    assert operations >= {
        ("/health", "get"),
        ("/tasks", "get"),
        ("/tasks", "post"),
        ("/tasks/{task_id}", "get"),
        ("/tasks/{task_id}", "patch"),
        ("/tasks/{task_id}", "delete"),
    }
