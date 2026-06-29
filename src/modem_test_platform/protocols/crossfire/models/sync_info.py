from dataclasses import dataclass


@dataclass(slots=True)
class SyncInfo:
    uid: str | None = None
    mode: str | None = None

    lq: int | None = None

    rssi: int | None = None

    snr: float | None = None

    noise: int | None = None

    frequency: int | None = None

    power: int | None = None

    firmware: str | None = None

    raw: str = ""