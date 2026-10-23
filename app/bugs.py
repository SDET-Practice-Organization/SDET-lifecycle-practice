"""Opt-in defects for practicing bug detection.

Enable with TASKAPP_BUGS=name1,name2 (or TASKAPP_BUGS=all). A good test suite
should fail for every bug listed here; CI verifies that it does.
"""

import os

KNOWN_BUGS = frozenset(
    {
        "create_returns_200",  # POST /tasks answers 200 instead of 201
        "patch_ignores_status",  # PATCH silently drops status changes
        "delete_not_persisted",  # DELETE answers 204 but keeps the task
        "filter_ignored",  # ?status= filter has no effect
        "pagination_off_by_one",  # ?offset= skips one extra item
    }
)


def _parse(raw: str) -> frozenset[str]:
    names = {name.strip() for name in raw.split(",") if name.strip()}
    if "all" in names:
        return KNOWN_BUGS
    unknown = names - KNOWN_BUGS
    if unknown:
        raise ValueError(f"Unknown TASKAPP_BUGS: {sorted(unknown)}. Known: {sorted(KNOWN_BUGS)}")
    return frozenset(names)


ACTIVE = _parse(os.environ.get("TASKAPP_BUGS", ""))


def enabled(name: str) -> bool:
    return name in ACTIVE
