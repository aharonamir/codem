from __future__ import annotations

from typing import Callable, Protocol

from codem.agents.validation import validate_planner_output


class LLMBackend(Protocol):
    """Protocol for the underlying LLM call."""

    def __call__(self, prompt: str) -> str:
        """Send a prompt and return the raw response string."""
        ...


def _stub_llm(prompt: str) -> str:
    """Placeholder LLM that returns a single milestone echoing the task."""
    import json

    return json.dumps({"milestones": [{"id": "1", "description": prompt}]})


class PlannerAgent:
    """Generates milestones from a task description.

    Input contract:  {"task": str, "repo_summary": str}
    Output contract: {"milestones": [{"id": str, "description": str}, ...]}
    """

    def __init__(self, llm: Callable[[str], str] | None = None) -> None:
        self._llm = llm or _stub_llm

    def generate(self, task: str, repo_summary: str = "") -> list[dict]:
        """Call the LLM and return validated milestones."""
        raw = self._llm(task)
        data = validate_planner_output(raw)
        return data["milestones"]
