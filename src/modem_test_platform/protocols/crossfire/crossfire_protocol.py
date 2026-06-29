from __future__ import annotations

import time

from modem_test_platform.transport.serial.serial_transport import SerialTransport


class CrossfireProtocol:
    """Обмен текстовыми командами с модемом."""

    def __init__(self, transport: SerialTransport):
        self.transport = transport

    def send_command(
            self,
            command: str,
            timeout: float = 0.5,
    ) -> str:

        self.transport.reset_input_buffer()

        self.transport.write((command.strip() + "\n").encode("utf-8"))

        time.sleep(0.05)

        response = ""
        start = time.time()

        while time.time() - start < timeout:

            data = self.transport.read(4096)

            if data:
                response += data.decode("utf-8", errors="ignore")
            else:
                time.sleep(0.05)

        if not response:
            return ""

        return response