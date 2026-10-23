"""Expected API contract, defined independently from the app's own models.

Validate with Model.model_validate_json(response.text): strict mode plus
extra="forbid" catches renamed, missing, added or wrongly typed fields.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TaskContract(_Strict):
    id: int
    title: str
    description: str | None
    status: Literal["todo", "in_progress", "done"]
    priority: int
    created_at: datetime
    updated_at: datetime


class TaskListContract(_Strict):
    items: list[TaskContract]
    total: int
    limit: int
    offset: int


class ErrorContract(_Strict):
    detail: str


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="allow")

    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorContract(_Strict):
    detail: list[ValidationIssue]


class HealthContract(_Strict):
    status: Literal["ok"]
    version: str


def issue_locations(body: dict[str, Any]) -> list[tuple[str | int, ...]]:
    """Locations of 422 validation issues, e.g. [("body", "title")]."""
    return [tuple(issue["loc"]) for issue in body["detail"]]
