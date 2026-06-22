"""
In-memory schema store.

For the MVP this is a plain dict — no persistence across restarts.
Swap this module for a Redis-backed implementation when you're ready
to scale; the interface stays identical.
"""
from typing import Any

_store: dict[str, dict[str, Any]] = {}


def save(schema_id: str, schema: dict[str, Any]) -> None:
    _store[schema_id] = schema


def get(schema_id: str) -> dict[str, Any] | None:
    return _store.get(schema_id)


def delete(schema_id: str) -> bool:
    if schema_id in _store:
        del _store[schema_id]
        return True
    return False


def list_ids() -> list[str]:
    return list(_store.keys())
