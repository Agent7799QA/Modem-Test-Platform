"""
Эмуляция команд через CRSF протокол.
Адаптирован из старого command_emulator.py (убраны Qt-зависимости).
"""

import time
import threading
from typing import List, Optional, Callable
from dataclasses import dataclass

from crossfire.crsf_parser.handling import crsf_build_frame
from crossfire.crsf_parser.payloads import PacketsTypes
from serial_protocol.serial_transport import SerialTransport


@dataclass
class EmulationConfig:
    """Конфигурация эмуляции."""
    frequency_hz: float = 1.0  # Частота отправки в Гц
    channels_count: int = 16  # Количество каналов
    min_value: int = 0  # Минимальное значение канала
    max_value: int = 2047  # Максимальное значение канала
    default_value: int = 1500  # Значение по умолчанию


class CommandEmulator:
    """
    Эмуляция команд через CRSF протокол.

    Отправляет RC-каналы в виде CRSF-фреймов через порт данных.
    Адаптирован из старого CommandEmulator.
    """

    def __init__(
            self,
            transport: SerialTransport,
            config: EmulationConfig = None,
    ):
        """
        Args:
            transport: Транспорт для отправки данных
            config: Конфигурация эмуляции
        """
        self.transport = transport
        self.config = config or EmulationConfig()

        # Состояние эмуляции
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._channels: List[int] = []
        self._command_count: int = 0

    def _build_frame(self, channels: List[int]) -> bytes:
        """
        Построить CRSF-фрейм с RC-каналами.

        Args:
            channels: Список из 16 значений каналов (0-2047)

        Returns:
            bytes: CRSF-фрейм
        """
        # Если каналов меньше 16, дополняем значением по умолчанию
        while len(channels) < 16:
            channels.append(self.config.default_value)

        # Обрезаем до 16 каналов
        channels = channels[:16]

        # Строим фрейм
        payload = {"channels": channels}
        frame = crsf_build_frame(PacketsTypes.RC_CHANNELS_PACKED, payload)
        return frame

    def _send_command(self, channels: List[int]) -> bool:
        """
        Отправить одну команду (один CRSF-фрейм).

        Args:
            channels: Список значений каналов

        Returns:
            True если отправка успешна
        """
        try:
            # Проверяем, что порт открыт
            if not self.transport.is_open:
                self.transport.open()

            # Строим и отправляем фрейм
            frame = self._build_frame(channels)
            self.transport.write(frame)
            self._command_count += 1
            return True

        except Exception as e:
            print(f"Error sending command: {e}")
            return False

    def _emulation_loop(self) -> None:
        """Основной цикл эмуляции."""
        while self._running:
            with self._lock:
                channels = self._channels.copy()

            if channels:
                self._send_command(channels)
            else:
                # Если каналы не заданы, используем значения по умолчанию
                default_channels = [self.config.default_value] * self.config.channels_count
                self._send_command(default_channels)

            # Ждем до следующей отправки
            time.sleep(1.0 / self.config.frequency_hz)

    # ========== Публичные методы ==========

    def send_once(self, channels: List[int]) -> bool:
        """
        Отправить команду один раз.

        Args:
            channels: Список значений каналов (до 16)

        Returns:
            True если отправка успешна
        """
        return self._send_command(channels)

    def start_emulation(self, channels: List[int], frequency_hz: float = None) -> None:
        """
        Начать эмуляцию команд с заданной частотой.

        Args:
            channels: Список значений каналов
            frequency_hz: Частота отправки в Гц (опционально)
        """
        if self._running:
            print("Emulation is already running")
            return

        with self._lock:
            self._channels = channels.copy()
            self._command_count = 0

        if frequency_hz is not None:
            self.config.frequency_hz = frequency_hz

        if self.config.frequency_hz <= 0:
            print(f"Frequency must be > 0, got {self.config.frequency_hz}")
            return

        self._running = True
        self._thread = threading.Thread(target=self._emulation_loop, daemon=True)
        self._thread.start()

        print(f"Emulation started: {len(channels)} channels, {self.config.frequency_hz} Hz")

    def stop_emulation(self) -> None:
        """Остановить эмуляцию."""
        if not self._running:
            return

        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            self._thread = None

        print(f"Emulation stopped. Commands sent: {self._command_count}")

    def update_channels(self, channels: List[int]) -> None:
        """
        Обновить значения каналов во время эмуляции.

        Args:
            channels: Новые значения каналов
        """
        with self._lock:
            self._channels = channels.copy()

    def is_running(self) -> bool:
        """Проверить, запущена ли эмуляция."""
        return self._running

    def get_command_count(self) -> int:
        """Получить количество отправленных команд."""
        return self._command_count

    def reset_count(self) -> None:
        """Сбросить счетчик отправленных команд."""
        self._command_count = 0


class CommandEmulatorWithCallback(CommandEmulator):
    """
    Расширенная версия CommandEmulator с callback'ами.
    """

    def __init__(
            self,
            transport: SerialTransport,
            on_send: Optional[Callable[[List[int], bytes], None]] = None,
            config: EmulationConfig = None,
    ):
        super().__init__(transport, config)
        self.on_send = on_send

    def _send_command(self, channels: List[int]) -> bool:
        """Отправить команду с callback."""
        try:
            frame = self._build_frame(channels)
            self.transport.write(frame)
            self._command_count += 1

            if self.on_send:
                self.on_send(channels, frame)

            return True

        except Exception as e:
            print(f"Error sending command: {e}")
            return False


def create_default_channels() -> List[int]:
    """
    Создать список каналов со значениями по умолчанию.

    Returns:
        List[int]: 16 каналов со значениями 1500
    """
    return [1500] * 16


def create_channels_from_pwm(pwm_values: List[int]) -> List[int]:
    """
    Преобразовать PWM значения (1000-2000) в значения CRSF (0-2047).

    Args:
        pwm_values: Список PWM значений (1000-2000)

    Returns:
        List[int]: CRSF значения каналов
    """
    crsf_values = []
    for pwm in pwm_values:
        # Конвертация: 1000-2000 → 0-2047
        crsf = int((pwm - 1000) / 1000 * 2047)
        crsf = max(0, min(2047, crsf))
        crsf_values.append(crsf)
    return crsf_values