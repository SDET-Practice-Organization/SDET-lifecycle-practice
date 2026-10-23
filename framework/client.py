import logging
from typing import Any

import requests

log = logging.getLogger("framework.http")


class ApiClient:
    """Thin HTTP layer: base URL, auth header, timeouts and request logging."""

    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if api_key is not None:
            self.session.headers["X-API-Key"] = api_key

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, f"{self.base_url}{path}", **kwargs)
        log.info("%s %s -> %s %s", method, path, response.status_code, response.text[:500])
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        self.session.close()


class TasksApi:
    """Domain wrapper for /tasks. Returns raw responses so tests own the assertions."""

    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, payload: dict[str, Any]) -> requests.Response:
        return self.client.post("/tasks", json=payload)

    def get(self, task_id: int | str) -> requests.Response:
        return self.client.get(f"/tasks/{task_id}")

    def list(self, **params: Any) -> requests.Response:
        return self.client.get("/tasks", params=params)

    def update(self, task_id: int | str, changes: dict[str, Any]) -> requests.Response:
        return self.client.patch(f"/tasks/{task_id}", json=changes)

    def delete(self, task_id: int | str) -> requests.Response:
        return self.client.delete(f"/tasks/{task_id}")
