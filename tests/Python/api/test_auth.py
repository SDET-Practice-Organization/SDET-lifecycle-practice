import pytest

from framework.assertions import assert_status
from framework.client import ApiClient
from framework.contracts import ErrorContract

PROTECTED_ENDPOINTS = [
    ("GET", "/tasks"),
    ("POST", "/tasks"),
    ("GET", "/tasks/1"),
    ("PATCH", "/tasks/1"),
    ("DELETE", "/tasks/1"),
]


@pytest.mark.parametrize(("method", "path"), PROTECTED_ENDPOINTS)
def test_missing_api_key_is_rejected(anonymous_client, method, path):
    response = anonymous_client.request(method, path, json={"title": "x"})

    assert_status(response, 401)
    ErrorContract.model_validate_json(response.text)


@pytest.mark.parametrize(("method", "path"), PROTECTED_ENDPOINTS)
def test_wrong_api_key_is_rejected(base_url, method, path):
    client = ApiClient(base_url, api_key="not-the-key")

    response = client.request(method, path, json={"title": "x"})

    assert_status(response, 401)
