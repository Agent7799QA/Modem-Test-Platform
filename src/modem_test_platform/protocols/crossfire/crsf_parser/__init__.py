"""
CRSF Parser - парсинг бинарного протокола Crossfire (CRSF).
Используется для приема телеметрии с порта данных (420000 бод).
"""

__version__ = "1.0.0"

import logging
from dataclasses import dataclass

from crossfire.crsf_parser.frames import crsf_frame, SYNC_RX_BYTE, SYNC_TX_BYTE
from enum import Enum
from typing import Callable, Container, Iterable, Tuple
from crossfire.crsf_parser.handling import crsf_frame_crc
from crossfire.crsf_parser.payloads import (
    PacketsTypes,
    PAYLOADS_SIZE,
)

from construct import (
    StreamError,
)

logger = logging.getLogger(__name__)

class PacketValidationStatus(Enum):
    VALID = 1
    UNKNOWN = 2
    INVALID = -1
    CRC = -2


@dataclass
class ProtocolStats:
    valid_frames: int = 0
    invalid_frames: int = 0
    crc_errors: int = 0
    framing_errors: int = 0


class CRSFParser:
    def __init__(
        self,
        consumer: Callable[
            [],
            Container,
        ],
    ) -> None:
        self._input = bytearray()
        self._consumer = consumer
        self._stats = ProtocolStats()
        pass

    def get_stats(self) -> ProtocolStats:
        return self._stats

    def _validate_packet(
        self, data: Iterable[int]
    ) -> Tuple[PacketValidationStatus, int, PacketsTypes]:
        size = data[0] - 2
        type = data[1]
        expected_size = PAYLOADS_SIZE.get(type, None)
        if not expected_size:
            return [PacketValidationStatus.UNKNOWN, size, type]
        if expected_size == size:
            return [PacketValidationStatus.VALID, size, type]
        return [PacketValidationStatus.INVALID, size, type]

    def parse_stream(self, input: bytearray) -> None:
        try:
            while len(input) > 0:
                val = input[0]
                if val == SYNC_TX_BYTE or val == SYNC_RX_BYTE:
                    status, size, frame_type = self._validate_packet(
                        [input[1], input[2]]
                    )
                    if status == PacketValidationStatus.VALID:
                        extra_data = 4
                        data = input[: size + extra_data]
                        content = crsf_frame.parse(data)
                        del input[: size + extra_data]
                        packet_crc = content.CRC
                        crc = crsf_frame_crc(data)
                        if crc != packet_crc:
                            status = PacketValidationStatus.CRC
                            self._stats.crc_errors += 1
                        else:
                            self._stats.valid_frames += 1
                        if self._consumer:
                            self._consumer(content, status)
                        continue
                    else:
                        self._stats.invalid_frames += 1
                else:
                    self._stats.framing_errors += 1
                del input[0]
        except IndexError:
            return
        except StreamError:
            return