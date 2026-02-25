from __future__ import annotations

from codem.agents.coder import CoderAgent
from codem.agents.planner import PlannerAgent
from codem.engine import ExecutionEngine
from codem.models.task import MAX_RETRIES, Task, TaskStatus


class Orchestrator:
    """DAG-based task orchestrator.

    Uses PlannerAgent to decompose a task into milestones, builds Task nodes,
    then executes them sequentially with CoderAgent + ExecutionEngine,
    respecting the max-retry policy.
    """

    def __init__(
        self,
        planner: PlannerAgent | None = None,
        coder: CoderAgent | None = None,
        engine: ExecutionEngine | None = None,
    ) -> None:
        self.tasks: list[Task] = []
        self.planner = planner or PlannerAgent()
        self.coder = coder or CoderAgent()
        self.engine = engine or ExecutionEngine()

    def plan(self, task: str, repo_summary: str = "") -> list[dict]:
        """Use PlannerAgent to generate milestones from a task description."""
        return self.planner.generate(task, repo_summary)

    def build_graph(self, milestones: list[dict]) -> None:
        """Convert planner milestones into Task nodes.

        Each milestone dict must have ``id`` and ``description`` keys,
        matching the Planner Agent output contract.
        """
        self.tasks = [
            Task(id=m["id"], description=m["description"])
            for m in milestones
        ]

    def run(self) -> bool:
        """Execute all tasks sequentially.

        For each task the CoderAgent generates a patch, the engine previews
        and applies it, then runs the test suite.  On failure the engine
        rolls back and we retry up to MAX_RETRIES times.  On success the
        changes are committed.

        Returns True if every task completed, False if any failed after
        exhausting retries.
        """
        for task in self.tasks:
            task.status = TaskStatus.IN_PROGRESS
            success = False

            for attempt in range(1, MAX_RETRIES + 1):
                task.attempts = attempt

                patch = self.coder.generate(
                    milestone_id=task.id,
                    description=task.description,
                )

                self.engine.preview_diff(patch)

                apply_result = self.engine.apply_patch(patch)
                if not apply_result.success:
                    self.engine.rollback()
                    continue

                test_result = self.engine.run_tests()
                if test_result.success:
                    self.engine.commit(f"codem: {task.description}")
                    success = True
                    break

                # tests failed – rollback and retry
                self.engine.rollback()

            if success:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
                return False

        return True
