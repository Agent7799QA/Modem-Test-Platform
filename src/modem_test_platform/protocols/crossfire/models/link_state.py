from dataclasses import dataclass, field

@dataclass(slots=True)
class LinkState:

    uplink_lq: int

    uplink_rssi: int

    downlink_lq: int

    downlink_rssi: int

    raw: str = field(default="", repr=False)