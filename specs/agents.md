# Agent Contracts
## Planner Agent
Input:
{
"task": "string",
"repo_summary": "string"
}

Output:
{
"milestones": [
{"id": "string", "description": "string"}
]
}

## Coder Agent
Input:
{
"milestone_id": "string",
"description": "string",
"files_context": ["string"]
}

Output:
{
"patch": "unified_diff_string"
}

STRICT RULE:
All outputs must be valid JSON.