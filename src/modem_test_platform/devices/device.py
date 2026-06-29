from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Device:
    """Базовая модель устройства."""

    id: str
    name: str
    port: str

    connected: bool = False