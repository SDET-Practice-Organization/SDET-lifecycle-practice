from typing import Any
from uuid import uuid4


def unique_tag(prefix: str = "t") -> str:
    """Short unique marker for isolating test data on a shared server."""
    return f"{prefix}-{uuid4().hex[:10]}"


def task_payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "title": f"task {unique_tag()}",
        "description": "created by automated test",
        "priority": 3,
    }
    payload.update(overrides)
    return payload
