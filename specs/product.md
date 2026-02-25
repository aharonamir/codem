# Codem Code – Product Specification (V1)

Codem Code is a terminal-first deterministic AI coding agent.

Goals:
- Accept natural language task
- Generate structured plan
- Execute minimal file diffs
- Run tests
- Auto-rollback on failure
- Commit successful changes

Non-Goals (V1):
- Multi-agent architecture
- Vector memory
- AST patching
- Plugin system

Core Principles:
- Deterministic execution
- No whole-file rewrites
- Explicit diffs only
- Git-based safety
- Bounded retries (max 3)

