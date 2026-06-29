import re

from modem_test_platform.protocols.crossfire.models.link_state import LinkState


class LinkStateParser:
    """Парсер ответа команды stat."""

    _PATTERN = re.compile(
        r"Uplink LQ:\s*(\d+),\s*"
        r"Uplink RSSI:\s*(-?\d+)\s*dBm,\s*"
        r"Downlink LQ:\s*(\d+),\s*"
        r"Downlink RSSI:\s*(-?\d+)\s*dBm",
        re.IGNORECASE,
    )

    def parse(self, response: str) -> LinkState:

        match = self._PATTERN.search(response)

        if match is None:
            raise ValueError("Invalid STAT response")

        return LinkState(
            uplink_lq=int(match.group(1)),
            uplink_rssi=int(match.group(2)),
            downlink_lq=int(match.group(3)),
            downlink_rssi=int(match.group(4)),
            raw=response,
        )