"""
Базовый класс для мониторинга порта данных.
Адаптирован из старого parser_base.py (убраны Qt-зависимости).
"""

import time
import threading
import serial
import platform
from typing import Optional, Callable, List
from dataclasses import dataclass

from modem_test_platform.transport.serial.serial_transport import SerialTransport


@dataclass
class MonitorConfig:
    """Конфигурация монитора."""
    baudrate: int = 420000
    bytesize: int = serial.EIGHTBITS
    parity: str = serial.PARITY_NONE
    stopbits: int = serial.STOPBITS_ONE
    read_timeout: float = 0.1


class BaseMonitor:
    """
    Базовый класс для мониторинга порта данных.

    Адаптирован из BaseParsingThread старого стенда.
    Убраны Qt-зависимости (QThread, Signal, QMutex, QTimer).

    Использует стандартные threading.Thread и callback-функции.
    """

    def __init__(
            self,
            port_name: str = None,
            on_data: Callable[[bytes], None] = None,
            on_status: Callable[[str], None] = None,
            config: MonitorConfig = None,
    ):
        """
        Args:
            port_name: Имя COM-порта
            on_data: Callback при получении данных (bytes)
            on_status: Callback при изменении статуса ("good" | "bad" | "closed")
            config: Конфигурация монитора
        """
        self.port_name = port_name
        self.on_data = on_data
        self.on_status = on_status
        self.config = config or MonitorConfig()

        # Состояние
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._serial_port: Optional[serial.Serial] = None
        self._port_set = False

        # Для эмуляции команд (запись в порт)
        self._write_command: Optional[bytes] = None
        self._write_interval: float = 0.0  # секунды
        self._write_timer: Optional[threading.Timer] = None
        self._is_writing = False

        # Статистика
        self._retries = 0
        self._max_retries = 500000000

        # Проверяем ОС для скорости
        self._check_os_baudrate()

    def _check_os_baudrate(self) -> None:
        """Проверить поддерживаемую скорость в зависимости от ОС."""
        try:
            if platform.system() == "Windows":
                self.config.baudrate = 420000
            elif platform.system() == "Darwin":
                self.config.baudrate = 450000
            else:
                self.config.baudrate = 420000
        except Exception as e:
            print(f"Error checking OS baudrate: {e}")

    def set_port(self, port_name: str) -> None:
        """Установить порт для мониторинга."""
        with self._lock:
            self.port_name = port_name
            self._port_set = True

    def _open_port(self) -> Optional[serial.Serial]:
        """Открыть порт для чтения данных."""
        try:
            ser = serial.Serial(
                port=self.port_name,
                baudrate=self.config.baudrate,
                bytesize=self.config.bytesize,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                timeout=self.config.read_timeout,
            )
            if self.on_status:
                self.on_status("good")
            return ser
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            if self.on_status:
                self.on_status("bad")
            return None

    def _close_port(self) -> None:
        """Закрыть порт."""
        if self._serial_port and self._serial_port.is_open:
            try:
                self._serial_port.close()
            except Exception as e:
                print(f"Error closing serial port: {e}")
            finally:
                self._serial_port = None
                if self.on_status:
                    self.on_status("closed")

    def _read_data(self) -> bytes:
        """Прочитать данные из порта."""
        if not self._serial_port or not self._serial_port.is_open:
            return b""
        try:
            return self._serial_port.read(100)
        except serial.SerialException as e:
            print(f"Read error: {e}")
            return b""

    def _write_data(self) -> None:
        """Записать данные в порт (для эмуляции команд)."""
        if not self._is_writing or not self._write_command:
            return

        if not self._serial_port or not self._serial_port.is_open:
            self._stop_writing()
            return

        try:
            self._serial_port.write(self._write_command)
        except serial.SerialException as e:
            print(f"Write error: {e}")
            self._stop_writing()
            if self.on_status:
                self.on_status("write_error")

    def _write_loop(self) -> None:
        """Цикл для периодической записи данных."""
        if not self._is_writing:
            return

        self._write_data()

        # Запланировать следующую запись
        if self._is_writing and self._write_interval > 0:
            self._write_timer = threading.Timer(self._write_interval, self._write_loop)
            self._write_timer.daemon = True
            self._write_timer.start()

    def start_writing(self, command: bytes, frequency_hz: float = 1.0) -> None:
        """
        Начать периодическую запись команды в порт.

        Args:
            command: Команда для записи (CRSF-фрейм)
            frequency_hz: Частота отправки в Гц
        """
        if frequency_hz <= 0:
            print(f"Frequency must be > 0, got {frequency_hz}")
            return

        self._write_command = command
        self._write_interval = 1.0 / frequency_hz
        self._is_writing = True

        # Остановить текущий таймер если есть
        if self._write_timer and self._write_timer.is_alive():
            self._write_timer.cancel()

        # Запустить новый цикл записи
        self._write_loop()

    def stop_writing(self) -> None:
        """Остановить периодическую запись."""
        self._is_writing = False
        self._write_command = None
        if self._write_timer and self._write_timer.is_alive():
            self._write_timer.cancel()
            self._write_timer = None

    def _monitor_loop(self) -> None:
        """Основной цикл мониторинга (выполняется в отдельном потоке)."""
        while self._running:
            try:
                # Если порт не установлен - ждем
                with self._lock:
                    if not self._port_set or not self.port_name:
                        time.sleep(0.1)
                        continue

                # Открываем порт если закрыт
                if self._serial_port is None or not self._serial_port.is_open:
                    self._serial_port = self._open_port()
                    if self._serial_port is None:
                        if self._retries >= self._max_retries:
                            print("Maximum retries reached. Exiting.")
                            break
                        self._retries += 1
                        time.sleep(0.05)
                        continue

                # Читаем данные
                data = self._read_data()
                if data and self.on_data:
                    self.on_data(data)

                # Сброс счетчика ретраев при успешном чтении
                self._retries = 0

            except serial.SerialException as e:
                print(f"Serial exception: {e}")
                self._close_port()
                if self._retries >= self._max_retries:
                    print("Maximum retries reached. Exiting.")
                    break
                self._retries += 1
                time.sleep(0.5)
            except Exception as e:
                print(f"Unexpected error in monitor loop: {e}")
                time.sleep(0.1)

    def start(self) -> None:
        """Запустить мониторинг в отдельном потоке."""
        if self._running:
            print("Monitor is already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print(f"Monitor started on port: {self.port_name}")

    def stop(self) -> None:
        """Остановить мониторинг."""
        self._running = False
        self.stop_writing()
        self._close_port()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            self._thread = None

        print("Monitor stopped")

    def is_running(self) -> bool:
        """Проверить, запущен ли мониторинг."""
        return self._running and self._thread and self._thread.is_alive()

    def is_port_open(self) -> bool:
        """Проверить, открыт ли порт."""
        return self._serial_port is not None and self._serial_port.is_open

    def write(self, data: bytes) -> int:
        """
        Написать данные в порт (однократно).

        Returns:
            Количество записанных байт
        """
        if not self._serial_port or not self._serial_port.is_open:
            raise serial.SerialException("Port is not open")
        return self._serial_port.write(data)