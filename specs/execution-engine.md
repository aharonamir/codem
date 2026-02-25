Rules:

* All file modifications must be unified diff patches.
* No full-file rewrites allowed.
* Patches must target existing files.
* Tests must run after each patch.
* On test failure:
    * Restore previous git state
    * Retry with reasoning context

Git Flow:
* Create branch: claudia/task-{uuid}
* Commit only after successful tests

