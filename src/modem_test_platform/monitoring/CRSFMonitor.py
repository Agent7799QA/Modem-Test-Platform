"""
Мониторинг порта данных с парсингом CRSF.
"""

from typing import Callable, Optional

from modem_test_platform.protocols.serial_protocol.serial_transport import SerialTransport
from modem_test_platform.protocols.crossfire.crsf_parser import (
    CRSFParser,
    PacketValidationStatus,
)


class CRSFMonitor:
    """Мониторинг порта данных с парсингом CRSF."""

    def __init__(self, transport: SerialTransport, on_frame: Optional[Callable] = None):
        self.transport = transport
        self.on_frame = on_frame  # callback при получении фрейма
        self.parser = CRSFParser(self._on_parsed_frame)
        self._running = False

    def start(self) -> None:
        """Запустить мониторинг."""
        self._running = True
        # TODO: реализовать цикл чтения

    def stop(self) -> None:
        """Остановить мониторинг."""
        self._running = False

    def _on_parsed_frame(self, frame, status) -> None:
        """Callback при распарсенном фрейме."""
        if status == PacketValidationStatus.VALID:
            if self.on_frame:
                self.on_frame(frame)