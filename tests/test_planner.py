import json

import pytest

from codem.agents.planner import PlannerAgent
from codem.agents.validation import SchemaValidationError


def test_default_stub_returns_milestone():
    agent = PlannerAgent()
    milestones = agent.generate("add login page")
    assert len(milestones) == 1
    assert milestones[0]["id"] == "1"
    assert milestones[0]["description"] == "add login page"


def test_custom_llm():
    def fake_llm(prompt: str) -> str:
        return json.dumps({
            "milestones": [
                {"id": "a", "description": "step a"},
                {"id": "b", "description": "step b"},
            ]
        })

    agent = PlannerAgent(llm=fake_llm)
    milestones = agent.generate("build feature")
    assert len(milestones) == 2
    assert milestones[0]["id"] == "a"
    assert milestones[1]["id"] == "b"


def test_invalid_llm_output_raises():
    agent = PlannerAgent(llm=lambda p: "not json")
    with pytest.raises(SchemaValidationError):
        agent.generate("anything")


def test_missing_milestones_key_raises():
    agent = PlannerAgent(llm=lambda p: '{"plans": []}')
    with pytest.raises(SchemaValidationError):
        agent.generate("anything")
