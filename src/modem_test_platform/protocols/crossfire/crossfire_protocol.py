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
        logger.debug(f"Отправка команды: '{command}'")

        try:
            if not self.transport.is_open:
                self.transport.open()
        except TransportConnectionError as e:
            logger.error(f"Не удалось открыть порт для команды '{command}': {e}")
            raise

        try:
            response = self.transport.send_command(command)
            # Логируем ответ (обрезаем если слишком длинный)
            if len(response) > 500:
                logger.debug(f"Ответ на '{command}': {response[:500]}... (всего {len(response)} байт)")
            else:
                logger.debug(f"Ответ на '{command}': {response}")
        except TransportConnectionError as e:
            logger.warning(f"Ошибка при отправке команды '{command}': {e}")
            if self._reconnect():
                logger.info(f"Повторная отправка команды '{command}' после переподключения")
                response = self.transport.send_command(command)
                if response.strip():
                    logger.debug(f"Ответ на '{command}' после переподключения: {response[:200]}")
                    return response
            raise

        if response.strip():
            return response

        logger.warning(f"Нет ответа на команду '{command}'")

        if self._reconnect():
            logger.info(f"Повторная отправка команды '{command}' после переподключения")
            response = self.transport.send_command(command)
            if response.strip():
                logger.debug(f"Ответ на '{command}' после переподключения: {response[:200]}")
                return response

        raise TransportConnectionError(
            f"Модем не отвечает на команду '{command}'. "
            f"Проверьте, что выбран порт управления."
        )

    def _check_connection(self) -> bool:
        """Проверить, жив ли модем через команду help."""
        try:
            logger.debug("Проверка соединения с модемом...")
            self.transport.reset_input_buffer()
            self.transport.write(b"help\r\n")
            time.sleep(0.2)
            response = self.transport.read(1024).decode("utf-8", errors="ignore")
            if "Drone RC" in response:
                logger.debug("Соединение с модемом установлено")
                return True
            logger.warning("Модем не отвечает на help")
            return False
        except Exception as e:
            logger.warning(f"Ошибка проверки соединения: {e}")
            return False

    def _reconnect(self) -> bool:
        """Попытка переподключения с экспоненциальной задержкой."""
        for attempt, delay in enumerate(self.reconnect_config.delays, 1):
            logger.warning(
                f"Попытка переподключения {attempt}/{len(self.reconnect_config.delays)} "
                f"(ждем {delay:.1f}с)"
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