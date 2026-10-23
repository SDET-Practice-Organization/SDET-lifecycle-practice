import requests


def assert_status(response: requests.Response, expected: int) -> None:
    """Status assertion whose failure message shows the request and response body."""
    __tracebackhide__ = True
    assert response.status_code == expected, (
        f"{response.request.method} {response.request.url}: "
        f"expected {expected}, got {response.status_code}\nBody: {response.text[:1000]}"
    )
