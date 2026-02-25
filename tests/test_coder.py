import json

import pytest

from codem.agents.coder import CoderAgent
from codem.agents.validation import SchemaValidationError


def test_default_stub_returns_empty_patch():
    agent = CoderAgent()
    patch = agent.generate(milestone_id="1", description="fix bug")
    assert patch == ""


def test_custom_llm():
    diff = "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new\n"

    def fake_llm(prompt: str) -> str:
        return json.dumps({"patch": diff})

    agent = CoderAgent(llm=fake_llm)
    patch = agent.generate(milestone_id="1", description="fix bug")
    assert patch == diff


def test_invalid_llm_output_raises():
    agent = CoderAgent(llm=lambda p: "not json")
    with pytest.raises(SchemaValidationError):
        agent.generate(milestone_id="1", description="x")


def test_missing_patch_key_raises():
    agent = CoderAgent(llm=lambda p: '{"diff": "..."}')
    with pytest.raises(SchemaValidationError):
        agent.generate(milestone_id="1", description="x")
