import pytest

from framework.assertions import assert_status
from framework.contracts import HealthContract


@pytest.mark.smoke
def test_health_is_ok_without_auth(anonymous_client):
    response = anonymous_client.get("/health")

    assert_status(response, 200)
    assert HealthContract.model_validate_json(response.text).status == "ok"
