from __future__ import annotations

import enum
import json
import uuid
from dataclasses import dataclass, field


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


MAX_RETRIES = 3


@dataclass
class Task:
    description: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "attempts": self.attempts,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            description=data["description"],
            status=TaskStatus(data["status"]),
            attempts=data.get("attempts", 0),
        )

    @classmethod
    def from_json(cls, raw: str) -> Task:
        return cls.from_dict(json.loads(raw))
