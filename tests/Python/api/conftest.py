from collections.abc import Callable, Iterator
from typing import Any

import pytest

from framework.client import ApiClient, TasksApi
from framework.config import Settings
from framework.factories import task_payload
from framework.server import running_app


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> Iterator[str]:
    """Target URL: API_BASE_URL if set, otherwise a local app started for this session.

    With pytest-xdist each worker starts its own instance.
    """
    if settings.base_url:
        yield settings.base_url
        return
    with running_app() as url:
        yield url


@pytest.fixture(scope="session")
def api_client(base_url: str, settings: Settings) -> Iterator[ApiClient]:
    client = ApiClient(base_url, settings.api_key, settings.timeout)
    yield client
    client.close()


@pytest.fixture
def anonymous_client(base_url: str, settings: Settings) -> Iterator[ApiClient]:
    client = ApiClient(base_url, api_key=None, timeout=settings.timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def tasks_api(api_client: ApiClient) -> TasksApi:
    return TasksApi(api_client)


@pytest.fixture
def create_task(tasks_api: TasksApi) -> Iterator[Callable[..., dict[str, Any]]]:
    """Factory that creates tasks through the API and deletes them after the test."""
    created: list[int] = []

    def _create(**overrides: Any) -> dict[str, Any]:
        response = tasks_api.create(task_payload(**overrides))
        # The exact status code is asserted in the create tests; setup only needs success.
        assert response.ok, f"Task setup failed: {response.status_code} {response.text}"
        task = response.json()
        created.append(task["id"])
        return task

    yield _create

    for task_id in created:
        tasks_api.delete(task_id)  # 404 is fine: the test may have deleted it already
