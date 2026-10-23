import pytest

from app.models import TaskCreate, TaskStatus
from app.store import TaskStore


@pytest.fixture
def store() -> TaskStore:
    return TaskStore()


def make(store: TaskStore, title: str, status: TaskStatus = TaskStatus.TODO):
    return store.create(TaskCreate(title=title, status=status))


def test_create_assigns_incrementing_ids(store):
    first, second = make(store, "a"), make(store, "b")
    assert (first.id, second.id) == (1, 2)
    assert first.created_at == first.updated_at


def test_get_missing_returns_none(store):
    assert store.get(999) is None


def test_list_filters_by_status_and_query(store):
    make(store, "Write report", TaskStatus.DONE)
    make(store, "Write tests", TaskStatus.TODO)
    make(store, "Review PR", TaskStatus.DONE)

    items, total = store.list(status=TaskStatus.DONE, query="write")

    assert total == 1
    assert [t.title for t in items] == ["Write report"]


def test_list_paginates(store):
    for i in range(5):
        make(store, f"task {i}")

    items, total = store.list(limit=2, offset=2)

    assert total == 5
    assert [t.title for t in items] == ["task 2", "task 3"]


def test_update_changes_fields_and_timestamp(store):
    task = make(store, "old")

    updated = store.update(task.id, {"title": "new"})

    assert updated.title == "new"
    assert updated.updated_at >= task.updated_at
    assert store.get(task.id) == updated


def test_update_missing_returns_none(store):
    assert store.update(999, {"title": "x"}) is None


def test_delete(store):
    task = make(store, "a")
    assert store.delete(task.id) is True
    assert store.delete(task.id) is False
    assert store.get(task.id) is None
