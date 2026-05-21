from pathlib import Path

import pytest

from task_tracker_mcp.storage import TaskStore


@pytest.fixture()
def store(tmp_path: Path) -> TaskStore:
    return TaskStore(tmp_path / "tasks.json")


def test_add_then_list_open(store: TaskStore) -> None:
    a = store.add("write tests")
    b = store.add("ship it", notes="after review")
    assert a.id == 1 and b.id == 2
    assert [t.id for t in store.list()] == [1, 2]
    assert b.notes == "after review"


def test_complete_and_filter(store: TaskStore) -> None:
    store.add("a")
    store.add("b")
    store.complete(1)
    assert [t.id for t in store.list("open")] == [2]
    assert [t.id for t in store.list("done")] == [1]
    assert [t.id for t in store.list("all")] == [1, 2]


def test_update_changes_fields(store: TaskStore) -> None:
    store.add("old title", notes="old notes")
    updated = store.update(1, title="new title")
    assert updated.title == "new title"
    assert updated.notes == "old notes"


def test_delete_removes_task(store: TaskStore) -> None:
    store.add("a")
    store.add("b")
    store.delete(1)
    assert [t.id for t in store.list("all")] == [2]


def test_clear_completed(store: TaskStore) -> None:
    store.add("a")
    store.add("b")
    store.complete(1)
    assert store.clear_done() == 1
    assert [t.id for t in store.list("all")] == [2]


def test_missing_task_raises(store: TaskStore) -> None:
    with pytest.raises(KeyError):
        store.complete(999)


def test_persists_across_instances(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    TaskStore(path).add("survive restart")
    reloaded = TaskStore(path).list("all")
    assert [t.title for t in reloaded] == ["survive restart"]
