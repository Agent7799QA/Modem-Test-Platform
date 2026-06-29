from __future__ import annotations

from typing import Optional

import serial


class SerialTransport:
    """Низкоуровневая работа с последовательным портом."""

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 1.0,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self._serial: Optional[serial.Serial] = None

    @property
    def is_open(self) -> bool:
        return (
            self._serial is not None
            and self._serial.is_open
        )

    def open(self) -> None:
        if self.is_open:
            return

        self._serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )

    def close(self) -> None:
        if self.is_open:
            self._serial.close()

    def write(self, data: bytes) -> None:
        if not self.is_open:
            raise RuntimeError("Serial port is closed")

        self._serial.write(data)

    def read(self, size: int = 1) -> bytes:
        if not self.is_open:
            raise RuntimeError("Serial port is closed")

        return self._serial.read(size)

    def readline(self) -> bytes:
        if not self.is_open:
            raise RuntimeError("Serial port is closed")

        return self._serial.readline()

    def reset_input_buffer(self) -> None:
        if self.is_open:
            self._serial.reset_input_buffer()

    def reset_output_buffer(self) -> None:
        if self.is_open:
            self._serial.reset_output_buffer()