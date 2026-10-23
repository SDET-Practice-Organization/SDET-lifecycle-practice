import pytest

from framework.assertions import assert_status
from framework.factories import unique_tag

# The server is shared with other tests (and with other xdist workers when API_BASE_URL
# is set), so every test scopes its listing to its own data with a unique title tag (?q=).


@pytest.fixture
def tag() -> str:
    return unique_tag("list")


def ids(response) -> list[int]:
    return [item["id"] for item in response.json()["items"]]


def test_list_returns_created_tasks_in_creation_order(create_task, tasks_api, tag):
    created = [create_task(title=f"{tag} {i}")["id"] for i in range(3)]

    response = tasks_api.list(q=tag)

    assert_status(response, 200)
    assert ids(response) == created
    assert response.json()["total"] == 3


def test_search_is_case_insensitive(create_task, tasks_api, tag):
    task = create_task(title=f"{tag} MixedCase")

    response = tasks_api.list(q=f"{tag} mixedcase".upper())

    assert ids(response) == [task["id"]]


@pytest.mark.parametrize("status", ["todo", "in_progress", "done"])
def test_filter_by_status(create_task, tasks_api, tag, status):
    tasks = {s: create_task(title=f"{tag} {s}", status=s) for s in ["todo", "in_progress", "done"]}

    response = tasks_api.list(q=tag, status=status)

    assert_status(response, 200)
    assert ids(response) == [tasks[status]["id"]]
    assert response.json()["total"] == 1


@pytest.mark.parametrize(
    ("limit", "offset", "start", "end"),
    [(2, 0, 0, 2), (2, 2, 2, 4), (2, 4, 4, 5), (10, 0, 0, 5), (2, 5, 5, 5)],
    ids=["first-page", "middle-page", "partial-last-page", "limit-above-total", "past-the-end"],
)
def test_pagination(create_task, tasks_api, tag, limit, offset, start, end):
    created = [create_task(title=f"{tag} {i}")["id"] for i in range(5)]

    response = tasks_api.list(q=tag, limit=limit, offset=offset)

    assert_status(response, 200)
    body = response.json()
    assert ids(response) == created[start:end]
    assert (body["total"], body["limit"], body["offset"]) == (5, limit, offset)


def test_pages_cover_all_items_without_overlap(create_task, tasks_api, tag):
    created = [create_task(title=f"{tag} {i}")["id"] for i in range(5)]

    seen = []
    for offset in range(0, 5, 2):
        seen += ids(tasks_api.list(q=tag, limit=2, offset=offset))

    assert seen == created
