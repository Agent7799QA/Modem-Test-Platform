import time
import logging

from modem_test_platform.transport.exceptions import TransportConnectionError
from modem_test_platform.protocols.crossfire.reconnect_config import ReconnectConfig
from modem_test_platform.transport.serial.serial_transport import SerialTransport

logger = logging.getLogger(__name__)


class CrossfireProtocol:
    """Обмен текстовыми командами с модемом."""

    # Команды, которые не возвращают данные (пустой ответ = успех)
    COMMANDS_WITHOUT_DATA = [
        "freq",
        "mode",
        "led",
        "reboot",
        "code",
        "attenuation",
        "rate",
        "pan",
        "bind",
        "fhss",
        "dsss",
        "timeslot",
        "protocol",
        "ewtests",
        "ttl",
        "ack",
    ]

    def __init__(self, transport: SerialTransport):
        self.transport = transport
        self.reconnect_config = ReconnectConfig()

    def _is_command_without_data(self, command: str) -> bool:
        """Проверить, является ли команда командой без данных."""
        return any(command.startswith(cmd) for cmd in self.COMMANDS_WITHOUT_DATA)

    def send_command(self, command: str, timeout: float = None) -> str:
        """
        Отправить команду модему.

        Args:
            command: Команда для отправки
            timeout: Таймаут ожидания ответа в секундах

        Returns:
            Ответ от модема (очищенный от эхо)

        Raises:
            TransportConnectionError: Если порт не открыт
        """
        # Проверяем, открыт ли порт
        if not self.transport.is_open:
            raise TransportConnectionError(
                f"Порт не открыт. Невозможно отправить команду '{command}'. "
                f"Сначала выполните подключение."
            )

        logger.info(f"Отправка команды: '{command}'")

        try:
            # Отправляем команду через транспорт
            if timeout is not None:
                response = self.transport.send_command(command, timeout=timeout)
            else:
                response = self.transport.send_command(command)

            # Логируем ответ (обрезаем если длинный)
            if len(response) > 500:
                logger.debug(
                    f"Ответ на '{command}': {response[:500]}... (всего {len(response)} байт)"
                )
            else:
                logger.debug(f"Ответ на '{command}': '{response}'")
        except TransportConnectionError as e:
            logger.error(f"Ошибка при отправке команды '{command}': {e}")
            raise

        # Для команд без данных пустой ответ = успех
        if self._is_command_without_data(command):
            logger.debug(f"Команда '{command}' выполнена (без данных)")
            return response

        # Для команд с данными (print, stat, ttlstat) проверяем наличие ответа
        if response.strip():
            return response

        # Если ответ пустой — просто возвращаем пустую строку
        # (не переподключаемся! порт должен быть открыт)
        logger.warning(f"Нет данных в ответе на команду '{command}'")
        return response

    def check_connection(self) -> bool:
        """
        Проверить соединение с модемом через команду help.

        Returns:
            True если модем отвечает
        """
        try:
            if not self.transport.is_open:
                logger.warning("Порт не открыт для проверки соединения")
                return False

            response = self.send_command("help", timeout=0.1)
            return "Drone RC" in response
        except Exception as e:
            logger.warning(f"Ошибка проверки соединения: {e}")
            return False

    def reopen(self) -> bool:
        """
        Переоткрыть порт (используется после ребута или при восстановлении).

        Returns:
            True если порт успешно открыт и модем отвечает
        """
        try:
            # Закрываем порт если открыт
            if self.transport.is_open:
                self.transport.close()
               # time.sleep(0.1)

            # Открываем заново
            self.transport.open()
            #time.sleep(0.5)

            # Проверяем соединение
            return self.check_connection()
        except Exception as e:
            logger.error(f"Ошибка переоткрытия порта: {e}")
            return False
