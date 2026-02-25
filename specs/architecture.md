# System Architecture

Terminal CLI
    ↓
Command Router
    ↓
Orchestrator (DAG-based)
    ↓
Planner Agent
    ↓
Coder Agent
    ↓
Execution Engine
    ↓
Git + Test Runner

# Execution Loop:

1. User submits task
2. Planner generates structured plan (JSON)
3. Orchestrator builds task graph
4. Coder generates patch diff
5. Diff preview shown
6. Apply patch
7. Run tests
8. If fail → rollback
9. Retry (max 3)
10. Commit on success
