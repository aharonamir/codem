import pytest

from codem.agents.validation import (
    SchemaValidationError,
    validate_coder_output,
    validate_json,
    validate_planner_output,
)


# --- validate_json ---


def test_validate_json_valid():
    assert validate_json('{"a": 1}') == {"a": 1}


def test_validate_json_invalid():
    with pytest.raises(SchemaValidationError, match="Invalid JSON"):
        validate_json("not json")


def test_validate_json_non_object():
    with pytest.raises(SchemaValidationError, match="Expected JSON object"):
        validate_json("[1, 2]")


# --- validate_planner_output ---


def test_planner_valid():
    raw = '{"milestones": [{"id": "1", "description": "do stuff"}]}'
    data = validate_planner_output(raw)
    assert len(data["milestones"]) == 1


def test_planner_empty_milestones():
    raw = '{"milestones": []}'
    data = validate_planner_output(raw)
    assert data["milestones"] == []


def test_planner_missing_milestones():
    with pytest.raises(SchemaValidationError, match="missing 'milestones'"):
        validate_planner_output('{"foo": 1}')


def test_planner_milestones_not_list():
    with pytest.raises(SchemaValidationError, match="must be a list"):
        validate_planner_output('{"milestones": "nope"}')


def test_planner_milestone_missing_id():
    with pytest.raises(SchemaValidationError, match="missing 'id'"):
        validate_planner_output('{"milestones": [{"description": "x"}]}')


def test_planner_milestone_missing_description():
    with pytest.raises(SchemaValidationError, match="missing 'description'"):
        validate_planner_output('{"milestones": [{"id": "1"}]}')


def test_planner_milestone_non_string_id():
    with pytest.raises(SchemaValidationError, match="must be a string"):
        validate_planner_output('{"milestones": [{"id": 1, "description": "x"}]}')


# --- validate_coder_output ---


def test_coder_valid():
    raw = '{"patch": "--- a/foo\\n+++ b/foo\\n"}'
    data = validate_coder_output(raw)
    assert "patch" in data


def test_coder_empty_patch():
    raw = '{"patch": ""}'
    data = validate_coder_output(raw)
    assert data["patch"] == ""


def test_coder_missing_patch():
    with pytest.raises(SchemaValidationError, match="missing 'patch'"):
        validate_coder_output('{"diff": "..."}')


def test_coder_patch_not_string():
    with pytest.raises(SchemaValidationError, match="must be a string"):
        validate_coder_output('{"patch": 123}')
