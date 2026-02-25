from __future__ import annotations

import subprocess
import uuid
from dataclasses import dataclass, field


@dataclass
class ExecutionResult:
    """Result of an execution step (matches execution_result.schema.json)."""

    success: bool
    logs: str = ""


class ExecutionEngine:
    """Applies unified-diff patches, manages git branches, and handles rollback.

    Rules (from spec):
    - All file modifications must be unified diff patches.
    - No full-file rewrites allowed.
    - Patches must target existing files.
    - Git branch: codem/task-{uuid}
    - Commit only after successful tests.
    - On failure: restore previous git state.
    """

    def __init__(self, repo_dir: str = ".") -> None:
        self.repo_dir = repo_dir
        self.branch_name: str | None = None
        self._original_branch: str | None = None

    # --- git helpers ---

    def _run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )

    def _current_branch(self) -> str:
        result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip()

    # --- public API ---

    def preview_diff(self, patch: str) -> str:
        """Return the patch string for display. No side effects."""
        return patch

    def create_branch(self) -> str:
        """Create and checkout a new branch: codem/task-{uuid}."""
        self._original_branch = self._current_branch()
        self.branch_name = f"codem/task-{uuid.uuid4().hex[:8]}"
        self._run_git("checkout", "-b", self.branch_name)
        return self.branch_name

    def apply_patch(self, patch: str) -> ExecutionResult:
        """Apply a unified diff patch via ``git apply``.

        Returns an ExecutionResult indicating success/failure.
        """
        if not patch:
            return ExecutionResult(success=True, logs="Empty patch, nothing to apply.")

        result = subprocess.run(
            ["git", "apply", "--verbose"],
            input=patch,
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return ExecutionResult(success=True, logs=result.stderr)
        return ExecutionResult(success=False, logs=result.stderr + result.stdout)

    def rollback(self) -> ExecutionResult:
        """Restore the working tree to a clean state.

        Discards uncommitted changes via ``git checkout -- .``.
        """
        result = self._run_git("checkout", "--", ".")
        if result.returncode == 0:
            return ExecutionResult(success=True, logs="Rolled back working tree.")
        return ExecutionResult(success=False, logs=result.stderr)

    def run_tests(self, test_cmd: str = "pytest") -> ExecutionResult:
        """Run the project test suite.

        Executes the given command in the repo directory and returns
        an ExecutionResult based on the exit code.
        """
        result = subprocess.run(
            test_cmd.split(),
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return ExecutionResult(success=True, logs=result.stdout)
        return ExecutionResult(
            success=False,
            logs=result.stdout + result.stderr,
        )

    def commit(self, message: str) -> ExecutionResult:
        """Stage all changes and commit."""
        self._run_git("add", ".")
        result = self._run_git("commit", "-m", message)
        if result.returncode == 0:
            return ExecutionResult(success=True, logs=result.stdout)
        return ExecutionResult(success=False, logs=result.stderr + result.stdout)
