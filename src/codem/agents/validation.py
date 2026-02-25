from __future__ import annotations

import json


class SchemaValidationError(Exception):
    """Raised when agent output fails schema validation."""


def validate_json(raw: str) -> dict:
    """Parse raw string as JSON, raising SchemaValidationError on failure."""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise SchemaValidationError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SchemaValidationError(f"Expected JSON object, got {type(data).__name__}")
    return data


def validate_planner_output(raw: str) -> dict:
    """Validate Planner Agent output against its contract.

    Expected shape:
        {"milestones": [{"id": "string", "description": "string"}, ...]}
    """
    data = validate_json(raw)
    if "milestones" not in data:
        raise SchemaValidationError("Planner output missing 'milestones' key")
    milestones = data["milestones"]
    if not isinstance(milestones, list):
        raise SchemaValidationError("'milestones' must be a list")
    for i, m in enumerate(milestones):
        if not isinstance(m, dict):
            raise SchemaValidationError(f"Milestone {i} is not an object")
        for key in ("id", "description"):
            if key not in m:
                raise SchemaValidationError(f"Milestone {i} missing '{key}'")
            if not isinstance(m[key], str):
                raise SchemaValidationError(f"Milestone {i} '{key}' must be a string")
    return data


def validate_coder_output(raw: str) -> dict:
    """Validate Coder Agent output against its contract.

    Expected shape:
        {"patch": "unified_diff_string"}
    """
    data = validate_json(raw)
    if "patch" not in data:
        raise SchemaValidationError("Coder output missing 'patch' key")
    if not isinstance(data["patch"], str):
        raise SchemaValidationError("'patch' must be a string")
    return data
