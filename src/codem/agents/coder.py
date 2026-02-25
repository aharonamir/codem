from __future__ import annotations

from typing import Callable, Protocol

from codem.agents.validation import validate_coder_output


class LLMBackend(Protocol):
    """Protocol for the underlying LLM call."""

    def __call__(self, prompt: str) -> str:
        """Send a prompt and return the raw response string."""
        ...


def _stub_llm(prompt: str) -> str:
    """Placeholder LLM that returns an empty patch."""
    import json

    return json.dumps({"patch": ""})


class CoderAgent:
    """Generates a unified diff patch for a single milestone.

    Input contract:  {"milestone_id": str, "description": str, "files_context": [str]}
    Output contract: {"patch": "unified_diff_string"}
    """

    def __init__(self, llm: Callable[[str], str] | None = None) -> None:
        self._llm = llm or _stub_llm

    def generate(
        self,
        milestone_id: str,
        description: str,
        files_context: list[str] | None = None,
    ) -> str:
        """Call the LLM and return a validated patch string."""
        raw = self._llm(description)
        data = validate_coder_output(raw)
        return data["patch"]
