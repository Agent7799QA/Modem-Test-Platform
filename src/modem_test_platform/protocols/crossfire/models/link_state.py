from dataclasses import dataclass


@dataclass(slots=True)
class LinkState:
    """Состояние радиолинии."""

    uplink_lq: int
    uplink_rssi: int

    downlink_lq: int
    downlink_rssi: int

    raw: str = ""