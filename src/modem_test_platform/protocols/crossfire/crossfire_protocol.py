from __future__ import annotations

import time
import logging

from modem_test_platform.transport.exceptions import TransportConnectionError
from modem_test_platform.protocols.crossfire.config import ReconnectConfig
from modem_test_platform.transport.serial.serial_transport import SerialTransport

logger = logging.getLogger(__name__)


class CrossfireProtocol:
    """Обмен текстовыми командами с модемом."""

    def __init__(self, transport: SerialTransport):
        self.transport = transport
        self.reconnect_config = ReconnectConfig()

    def send_command(self, command: str) -> str:
        """Отправить команду модему."""
        import time

        try:
            if not self.transport.is_open:
                self.transport.open()
                time.sleep(0.1)  # Дать время на инициализацию
        except TransportConnectionError as e:
            raise TransportConnectionError(
                f"Не удалось открыть порт для отправки команды '{command}': {e}"
            ) from e

        try:
            response = self.transport.send_command(command)
        except TransportConnectionError as e:
            logger.warning(f"Ошибка при отправке команды '{command}': {e}")
            if self._reconnect():
                response = self.transport.send_command(command)
                if response.strip():
                    return response
            raise

        if response.strip():
            return response

        logger.warning("Нет ответа на команду '%s'", command)

        if self._reconnect():
            response = self.transport.send_command(command)
            if response.strip():
                return response

        raise TransportConnectionError(
            f"Модем не отвечает на команду '{command}'. "
            f"Проверьте, что выбран порт управления."
        )

    def _check_connection(self) -> bool:
        """Проверить, жив ли модем через команду help."""
        try:
            self.transport.reset_input_buffer()
            self.transport.write(b"help\n")
            time.sleep(0.1)
            response = self.transport.read(1024).decode("utf-8", errors="ignore")
            return "Drone RC" in response
        except Exception:
            return False

    def _reconnect(self) -> bool:
        """Попытка переподключения с экспоненциальной задержкой."""
        for attempt, delay in enumerate(self.reconnect_config.delays, 1):
            logger.warning(
                f"Попытка переподключения {attempt}/{len(self.reconnect_config.delays)} "
                f"(ждем {delay:.0.5f}с)"
            )
            time.sleep(delay)

            try:
                self.transport.close()
                self.transport.open()
                if self._check_connection():
                    logger.info(f"✅ Переподключение успешно (попытка {attempt})")
                    return True
                logger.warning(f"⚠️ Модем не отвечает после подключения (попытка {attempt})")
            except TransportConnectionError as e:
                logger.warning(f"⚠️ Ошибка переподключения: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка переподключения: {e}")

        logger.error("❌ Не удалось переподключиться")
        return False