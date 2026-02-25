Test 1:
Input: "Add a hello world endpoint"
Expected:
- Planner produces at least 1 milestone
- Coder produces valid unified diff
- Tests pass
- Commit created

Test 2:
Force failing test
Expected:
- Rollback executed
- Retry triggered
- Max retry enforced
