import json

from codem.models.task import Task, TaskStatus


def test_task_default_values():
    t = Task(description="do something")
    assert t.description == "do something"
    assert t.status == TaskStatus.PENDING
    assert t.attempts == 0
    assert len(t.id) == 12


def test_task_explicit_values():
    t = Task(id="abc", description="fix bug", status=TaskStatus.IN_PROGRESS, attempts=2)
    assert t.id == "abc"
    assert t.status == TaskStatus.IN_PROGRESS
    assert t.attempts == 2


def test_to_dict():
    t = Task(id="t1", description="test task")
    d = t.to_dict()
    assert d == {
        "id": "t1",
        "description": "test task",
        "status": "pending",
        "attempts": 0,
    }


def test_to_json():
    t = Task(id="t1", description="test task")
    raw = t.to_json()
    parsed = json.loads(raw)
    assert parsed["id"] == "t1"
    assert parsed["status"] == "pending"


def test_from_dict():
    t = Task.from_dict({"id": "x", "description": "d", "status": "completed", "attempts": 3})
    assert t.id == "x"
    assert t.status == TaskStatus.COMPLETED
    assert t.attempts == 3


def test_from_dict_missing_attempts():
    t = Task.from_dict({"id": "x", "description": "d", "status": "pending"})
    assert t.attempts == 0


def test_roundtrip_json():
    original = Task(id="rt", description="roundtrip", status=TaskStatus.FAILED, attempts=2)
    restored = Task.from_json(original.to_json())
    assert restored.id == original.id
    assert restored.description == original.description
    assert restored.status == original.status
    assert restored.attempts == original.attempts


def test_status_values():
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.FAILED.value == "failed"
    assert TaskStatus.ROLLED_BACK.value == "rolled_back"
