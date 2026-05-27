from __future__ import annotations

from .base import Strategy


_REGISTRY: dict[str, type[Strategy]] = {}


def register(cls: type[Strategy]) -> type[Strategy]:
    _REGISTRY[cls.meta.id] = cls
    return cls


def all_strategies() -> list[type[Strategy]]:
    return list(_REGISTRY.values())


def get(strategy_id: str) -> type[Strategy] | None:
    return _REGISTRY.get(strategy_id)
