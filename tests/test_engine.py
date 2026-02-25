import os
import subprocess

import pytest

from codem.engine import ExecutionEngine, ExecutionResult


@pytest.fixture()
def git_repo(tmp_path):
    """Create a temporary git repo with one committed file."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path, capture_output=True,
    )

    hello = tmp_path / "hello.txt"
    hello.write_text("hello\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path, capture_output=True,
    )
    return tmp_path


# --- ExecutionResult ---


def test_execution_result_success():
    r = ExecutionResult(success=True, logs="ok")
    assert r.success is True
    assert r.logs == "ok"


def test_execution_result_defaults():
    r = ExecutionResult(success=False)
    assert r.logs == ""


# --- preview_diff ---


def test_preview_diff_returns_patch():
    engine = ExecutionEngine()
    patch = "--- a/f\n+++ b/f\n"
    assert engine.preview_diff(patch) == patch


# --- create_branch ---


def test_create_branch(git_repo):
    engine = ExecutionEngine(repo_dir=str(git_repo))
    branch = engine.create_branch()
    assert branch.startswith("codem/task-")

    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert result.stdout.strip() == branch


# --- apply_patch ---


def test_apply_patch_empty(git_repo):
    engine = ExecutionEngine(repo_dir=str(git_repo))
    r = engine.apply_patch("")
    assert r.success is True
    assert "Empty patch" in r.logs


def test_apply_patch_valid(git_repo):
    engine = ExecutionEngine(repo_dir=str(git_repo))
    patch = (
        "--- a/hello.txt\n"
        "+++ b/hello.txt\n"
        "@@ -1 +1 @@\n"
        "-hello\n"
        "+world\n"
    )
    r = engine.apply_patch(patch)
    assert r.success is True

    content = (git_repo / "hello.txt").read_text()
    assert content == "world\n"


def test_apply_patch_invalid(git_repo):
    engine = ExecutionEngine(repo_dir=str(git_repo))
    r = engine.apply_patch("garbage patch content")
    assert r.success is False


# --- rollback ---


def test_rollback(git_repo):
    engine = ExecutionEngine(repo_dir=str(git_repo))

    # modify file
    (git_repo / "hello.txt").write_text("modified\n")
    assert (git_repo / "hello.txt").read_text() == "modified\n"

    r = engine.rollback()
    assert r.success is True
    assert (git_repo / "hello.txt").read_text() == "hello\n"


# --- commit ---


def test_commit(git_repo):
    engine = ExecutionEngine(repo_dir=str(git_repo))

    (git_repo / "hello.txt").write_text("committed\n")
    r = engine.commit("test commit")
    assert r.success is True

    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert "test commit" in log.stdout


# --- integration: apply then rollback ---


def test_apply_then_rollback(git_repo):
    engine = ExecutionEngine(repo_dir=str(git_repo))
    patch = (
        "--- a/hello.txt\n"
        "+++ b/hello.txt\n"
        "@@ -1 +1 @@\n"
        "-hello\n"
        "+changed\n"
    )
    engine.apply_patch(patch)
    assert (git_repo / "hello.txt").read_text() == "changed\n"

    engine.rollback()
    assert (git_repo / "hello.txt").read_text() == "hello\n"
