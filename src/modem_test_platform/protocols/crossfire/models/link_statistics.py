from dataclasses import dataclass


@dataclass(slots=True)
class LinkStatistics:

    uplink_lq: int | None = None

    uplink_rssi: int | None = None

    downlink_lq: int | None = None

    downlink_rssi: int | None = None

    raw: str = ""