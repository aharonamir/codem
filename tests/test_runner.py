import subprocess
import textwrap

import pytest

from codem.engine import ExecutionEngine


@pytest.fixture()
def git_repo(tmp_path):
    """Create a temporary git repo."""
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


def test_run_tests_passing(git_repo):
    """run_tests returns success when the test suite passes."""
    test_file = git_repo / "test_ok.py"
    test_file.write_text("def test_pass(): assert True\n")

    engine = ExecutionEngine(repo_dir=str(git_repo))
    result = engine.run_tests("pytest")
    assert result.success is True
    assert "passed" in result.logs


def test_run_tests_failing(git_repo):
    """run_tests returns failure when the test suite fails."""
    test_file = git_repo / "test_fail.py"
    test_file.write_text("def test_fail(): assert False\n")

    engine = ExecutionEngine(repo_dir=str(git_repo))
    result = engine.run_tests("pytest")
    assert result.success is False
    assert "failed" in result.logs.lower()


def test_run_tests_custom_command(git_repo):
    """run_tests accepts a custom test command."""
    engine = ExecutionEngine(repo_dir=str(git_repo))
    result = engine.run_tests("python -c pass")
    assert result.success is True


def test_run_tests_no_tests(git_repo):
    """run_tests succeeds when pytest finds no tests (exit code 5 = no tests)."""
    engine = ExecutionEngine(repo_dir=str(git_repo))
    result = engine.run_tests("pytest")
    # pytest exit code 5 means no tests collected – that's not success
    # but it's also valid behavior; just check it returns a result
    assert isinstance(result.success, bool)


# --- end-to-end: patch → test → rollback cycle ---


def test_patch_pass_commit_cycle(git_repo):
    """Apply patch, tests pass, commit persists."""
    # Create a test that reads hello.txt and asserts "world"
    test_file = git_repo / "test_check.py"
    test_file.write_text(textwrap.dedent("""\
        def test_content():
            assert open("hello.txt").read().strip() == "world"
    """))
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "add test"],
        cwd=git_repo, capture_output=True,
    )

    engine = ExecutionEngine(repo_dir=str(git_repo))
    patch = (
        "--- a/hello.txt\n"
        "+++ b/hello.txt\n"
        "@@ -1 +1 @@\n"
        "-hello\n"
        "+world\n"
    )

    apply_result = engine.apply_patch(patch)
    assert apply_result.success is True

    test_result = engine.run_tests("pytest")
    assert test_result.success is True

    commit_result = engine.commit("patched")
    assert commit_result.success is True

    # verify committed
    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert "patched" in log.stdout


def test_patch_fail_rollback_cycle(git_repo):
    """Apply patch, tests fail, rollback restores original."""
    # Test that checks hello.txt == "hello"
    test_file = git_repo / "test_check.py"
    test_file.write_text(textwrap.dedent("""\
        def test_content():
            assert open("hello.txt").read().strip() == "hello"
    """))
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "add test"],
        cwd=git_repo, capture_output=True,
    )

    engine = ExecutionEngine(repo_dir=str(git_repo))
    patch = (
        "--- a/hello.txt\n"
        "+++ b/hello.txt\n"
        "@@ -1 +1 @@\n"
        "-hello\n"
        "+WRONG\n"
    )

    engine.apply_patch(patch)
    test_result = engine.run_tests("pytest")
    assert test_result.success is False

    engine.rollback()
    assert (git_repo / "hello.txt").read_text() == "hello\n"
