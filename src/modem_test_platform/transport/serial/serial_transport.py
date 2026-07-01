import time
import serial
from serial import SerialException
from modem_test_platform.transport.exceptions import TransportConnectionError
import logging

logger = logging.getLogger(__name__)


class SerialTransport:
    """Транспорт для работы с последовательным портом."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None

    def open(self) -> None:
        """Открыть последовательный порт."""
        if self.is_open:
            return

        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                write_timeout=self.timeout,
            )
            # Небольшая задержка для инициализации порта
            #time.sleep(0.1)
        except SerialException as e:
            error_msg = str(e).lower()
            if "access is denied" in error_msg or "permissionerror" in error_msg:
                raise TransportConnectionError(
                    f"Порт '{self.port}' занят. Возможно, он уже используется другим приложением. "
                    f"Закройте все программы, использующие этот порт, и попробуйте снова."
                ) from e
            elif "port not found" in error_msg or "does not exist" in error_msg:
                raise TransportConnectionError(
                    f"Порт '{self.port}' не найден. Проверьте подключение модема."
                ) from e
            else:
                raise TransportConnectionError(
                    f"Не удалось открыть порт '{self.port}': {e}"
                ) from e

    def close(self) -> None:
        """Закрыть последовательный порт."""
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
            self._serial = None

    @property
    def is_open(self) -> bool:
        """Проверить, открыт ли порт."""
        return self._serial is not None and self._serial.is_open

    def write(self, data: bytes) -> int:
        """Записать данные в порт."""
        if not self.is_open:
            raise TransportConnectionError("Порт не открыт")
        return self._serial.write(data)

    def read(self, size: int = 1) -> bytes:
        """Прочитать данные из порта."""
        if not self.is_open:
            raise TransportConnectionError("Порт не открыт")
        return self._serial.read(size)

    def reset_input_buffer(self) -> None:
        """Очистить входной буфер."""
        if self.is_open:
            self._serial.reset_input_buffer()

    def reset_output_buffer(self) -> None:
        """Очистить выходной буфер."""
        if self.is_open:
            self._serial.reset_output_buffer()

    def send_command(self, command: str, timeout: float = None) -> str:
        """
        Отправить команду и получить ответ.
        """
        if not self.is_open:
            raise TransportConnectionError("Порт не открыт")

        # Очистить буферы
        self.reset_input_buffer()
        self.reset_output_buffer()

        # Отправить команду с \r\n
        self.write(f"{command}\r\n".encode("utf-8"))

        # Дать время модему на обработку
        #time.sleep(0.1)

        # Сохраняем оригинальный таймаут
        original_timeout = self._serial.timeout if self._serial else None
        if timeout is not None:
            self._serial.timeout = timeout

        try:
            response = b""
            while True:
                data = self._serial.read(4096)
                if not data:
                    break
                response += data

                text = data.decode("utf-8", errors="ignore")

                # ✅ Единственный надежный маркер окончания - ".."
                if ".." in text:
                    # Даем время для получения остальных данных
                    time.sleep(0.05)
                    if self._serial.in_waiting == 0:
                        break
        finally:
            if timeout is not None and original_timeout is not None:
                self._serial.timeout = original_timeout

        response_text = response.decode("utf-8", errors="ignore")
        logger.info("Ответ на команду mode %s:\n%s", "stat", response_text)

        # Очищаем ответ от эха команды
        lines = response_text.splitlines()
        cleaned_lines = []
        skip_echo = True

        for line in lines:
            stripped = line.strip()

            # Пропускаем эхо команды
            if skip_echo:
                # Эхо может быть: "freq 4500" или "> print" или "> " или просто ">"
                if stripped == command:
                    continue
                if stripped == f"> {command}":
                    continue
                if stripped == ">":
                    continue
                if stripped == "..":
                    continue

                # Если строка с данными - начинаем собирать
                if stripped and not stripped.startswith(">"):
                    skip_echo = False
                    # Убираем ".." если есть в конце
                    if stripped.endswith(".."):
                        stripped = stripped[:-2]
                    cleaned_lines.append(stripped)
                elif stripped.startswith(">") and len(stripped) > 1:
                    # Это может быть "> data" - убираем "> "
                    skip_echo = False
                    data_part = stripped[1:].strip()
                    if data_part.endswith(".."):
                        data_part = data_part[:-2]
                    if data_part:
                        cleaned_lines.append(data_part)
            else:
                # Убираем ">" в начале строки если есть
                if stripped.startswith(">"):
                    if stripped == ">":
                        continue
                    stripped = stripped[1:].strip()
                # Убираем ".." в конце
                if stripped.endswith(".."):
                    stripped = stripped[:-2]
                if stripped:
                    cleaned_lines.append(stripped)

        response_text = "\n".join(cleaned_lines).strip()

        # Для команд без данных (freq, mode, led) ответ может быть пустым
        return response_text