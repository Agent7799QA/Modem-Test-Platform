"""
Serial транспорт для работы с COM-портом.
"""

import time
import logging
import serial
from typing import Optional

from modem_test_platform.transport.exceptions import TransportConnectionError

logger = logging.getLogger(__name__)


class SerialTransport:
    """Реализация транспорта через последовательный порт."""

    def __init__(self, port: str, baudrate: int = 420000, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.is_open = False

    def open(self) -> None:
        if self.is_open:
            return

        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout,
            )
            self.is_open = True
            logger.info(f"✅ Порт {self.port} открыт")
        except Exception as e:
            raise TransportConnectionError(f"Не удалось открыть порт {self.port}: {e}")

    def close(self) -> None:
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.is_open = False
        logger.info(f"Порт {self.port} закрыт")

    def send_command(self, command: str, timeout: float = None) -> str:
        if not self.is_open:
            raise TransportConnectionError("Порт не открыт")

        if timeout is None:
            timeout = self.timeout

        # Отправляем команду
        command_line = command + '\r\n'
        logger.debug(f"Отправка команды: {command_line!r}")

        try:
            self.serial.write(command_line.encode('utf-8'))
            self.serial.flush()
        except Exception as e:
            raise TransportConnectionError(f"Ошибка отправки команды: {e}")

        # Читаем ответ
        response = self._read_response(timeout)
        logger.debug(f"Ответ: {response!r}")

        return response

    def _read_response(self, timeout: float) -> str:
        lines = []
        start_time = time.time()

        while True:
            if (time.time() - start_time) > timeout:
                logger.warning(f"Таймаут чтения ответа ({timeout}с)")
                break

            if self.serial.in_waiting > 0:
                try:
                    line = self.serial.readline()
                    if not line:
                        continue

                    decoded = line.decode('utf-8', errors='ignore').strip()
                    lines.append(decoded)

                    # Конец ответа - приглашение модема
                    if decoded.endswith('> '):
                        break
                except Exception as e:
                    logger.error(f"Ошибка чтения: {e}")
                    break
            else:
                time.sleep(0.01)

        return '\n'.join(lines)

    def read(self, size: int = 1) -> bytes:
        if not self.is_open:
            raise TransportConnectionError("Порт не открыт")
        return self.serial.read(size)

    def write(self, data: bytes) -> int:
        if not self.is_open:
            raise TransportConnectionError("Порт не открыт")
        return self.serial.write(data)

    @property
    def in_waiting(self) -> int:
        if not self.is_open or self.serial is None:
            return 0
        return self.serial.in_waiting