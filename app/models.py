from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

Title = Annotated[str, Field(min_length=1, max_length=200)]
Description = Annotated[str, Field(max_length=2000)]
Priority = Annotated[int, Field(ge=1, le=5)]


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: Title
    description: Description | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = 3


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: Title | None = None
    description: Description | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None

    @model_validator(mode="after")
    def reject_nulls(self) -> "TaskUpdate":
        # Only description may be cleared with an explicit null.
        nulls = [
            f for f in self.model_fields_set if f != "description" and getattr(self, f) is None
        ]
        if nulls:
            raise ValueError(f"Fields cannot be null: {sorted(nulls)}")
        return self


class Task(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    created_at: datetime
    updated_at: datetime


class TaskList(BaseModel):
    items: list[Task]
    total: int
    limit: int
    offset: int
