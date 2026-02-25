from unittest.mock import MagicMock

from codem.engine import ExecutionEngine, ExecutionResult
from codem.models.task import Task, TaskStatus
from codem.orchestrator import Orchestrator


def _make_engine(test_success: bool = True) -> ExecutionEngine:
    """Build a mock engine whose run_tests returns the given result."""
    engine = MagicMock(spec=ExecutionEngine)
    engine.preview_diff.return_value = ""
    engine.apply_patch.return_value = ExecutionResult(success=True)
    engine.run_tests.return_value = ExecutionResult(success=test_success)
    engine.commit.return_value = ExecutionResult(success=True)
    engine.rollback.return_value = ExecutionResult(success=True)
    return engine


def test_build_graph():
    o = Orchestrator()
    o.build_graph([
        {"id": "m1", "description": "first milestone"},
        {"id": "m2", "description": "second milestone"},
    ])
    assert len(o.tasks) == 2
    assert o.tasks[0].id == "m1"
    assert o.tasks[1].id == "m2"
    assert all(t.status == TaskStatus.PENDING for t in o.tasks)


def test_run_all_succeed():
    engine = _make_engine(test_success=True)
    o = Orchestrator(engine=engine)
    o.build_graph([
        {"id": "1", "description": "a"},
        {"id": "2", "description": "b"},
    ])
    assert o.run() is True
    assert all(t.status == TaskStatus.COMPLETED for t in o.tasks)
    assert all(t.attempts == 1 for t in o.tasks)
    assert engine.commit.call_count == 2


def test_run_first_fails_exhausts_retries():
    engine = _make_engine(test_success=False)
    o = Orchestrator(engine=engine)
    o.build_graph([
        {"id": "1", "description": "a"},
        {"id": "2", "description": "b"},
    ])
    assert o.run() is False
    assert o.tasks[0].status == TaskStatus.FAILED
    assert o.tasks[0].attempts == 3
    # second task never ran
    assert o.tasks[1].status == TaskStatus.PENDING
    assert engine.rollback.call_count == 3


def test_retry_then_succeed():
    engine = _make_engine()
    call_count = 0

    def flaky_tests():
        nonlocal call_count
        call_count += 1
        return ExecutionResult(success=call_count >= 2)

    engine.run_tests.side_effect = lambda: flaky_tests()

    o = Orchestrator(engine=engine)
    o.build_graph([{"id": "1", "description": "flaky task"}])
    assert o.run() is True
    assert o.tasks[0].status == TaskStatus.COMPLETED
    assert o.tasks[0].attempts == 2


def test_max_retries_is_three():
    engine = _make_engine(test_success=False)
    o = Orchestrator(engine=engine)
    o.build_graph([{"id": "1", "description": "doomed"}])
    o.run()
    assert engine.run_tests.call_count == 3
    assert engine.rollback.call_count == 3
    assert o.tasks[0].attempts == 3


def test_empty_graph():
    o = Orchestrator()
    assert o.run() is True


def test_commit_on_success():
    engine = _make_engine(test_success=True)
    o = Orchestrator(engine=engine)
    o.build_graph([{"id": "1", "description": "good task"}])
    o.run()
    engine.commit.assert_called_once_with("codem: good task")


def test_no_commit_on_failure():
    engine = _make_engine(test_success=False)
    o = Orchestrator(engine=engine)
    o.build_graph([{"id": "1", "description": "bad task"}])
    o.run()
    engine.commit.assert_not_called()
