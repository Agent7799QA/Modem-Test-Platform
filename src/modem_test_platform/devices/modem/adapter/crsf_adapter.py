"""
Адаптер для работы с портом данных (CRSF протокол).
Инкапсулирует мониторинг телеметрии и эмуляцию команд.
"""
import logging
from typing import List, Optional, Callable

from modem_test_platform.monitoring.rx_monitor import RxMonitor, LinkState
from modem_test_platform.monitoring.base_monitor import BaseMonitor, MonitorConfig
from modem_test_platform.emulation.command_emulator import CommandEmulator, EmulationConfig
from modem_test_platform.protocols.serial_protocol.serial_transport import SerialTransport

logger = logging.getLogger(__name__)

class CRSFAdapter:
    """
    Адаптер для CRSF порта данных.

    Обеспечивает:
    - Мониторинг телеметрии (LQ, RSSI)
    - Эмуляцию RC-команд (отправка CRSF-фреймов)
    """

    def __init__(self, transport: SerialTransport):
        """
        Args:
            transport: Открытый или готовый к открытию SerialTransport для порта данных
        """
        self.transport = transport
        self._monitor: Optional[RxMonitor] = None
        self._emulator: Optional[CommandEmulator] = None
        self._is_monitoring = False
        self._is_emulating = False

    def start_monitoring(
        self,
        on_link_state: Callable[[LinkState], None],
        on_status: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Запустить мониторинг телеметрии.

        Args:
            on_link_state: Callback при получении LinkState
            on_status: Callback при изменении статуса порта
        """
        if self._is_monitoring:
            print("Мониторинг уже запущен")
            return

        # Убедимся, что транспорт открыт
        if not self.transport.is_open:
            self.transport.open()

        # Создаём базовый монитор с внешним транспортом
        base_monitor = BaseMonitor(
            on_status=on_status,
            config=MonitorConfig(baudrate=self.transport.baudrate),
        )
        base_monitor.set_transport(self.transport)

        # Создаём RxMonitor с переданным монитором
        self._monitor = RxMonitor(
            monitor=base_monitor,
            on_link_state=on_link_state,
            on_status=on_status,
        )

        self._monitor.start()
        self._is_monitoring = True
        print("Мониторинг CRSF запущен")

    def stop_monitoring(self) -> None:
        """Остановить мониторинг телеметрии."""
        if not self._is_monitoring:
            return
        if self._monitor:
            self._monitor.stop()
            self._monitor = None
        self._is_monitoring = False
        print("Мониторинг CRSF остановлен")

    def send_rc_channels(self, channels: List[int]) -> bool:
        """
        Отправить один CRSF-фрейм с RC-каналами.

        Args:
            channels: Список значений каналов (до 16, 0-2047)

        Returns:
            True если отправка успешна
        """
        if not self.transport.is_open:
            self.transport.open()

        # Создаём эмулятор и отправляем один раз
        emulator = CommandEmulator(self.transport)
        return emulator.send_once(channels)

    def start_emulation(
        self,
        channels: List[int],
        frequency_hz: float = 10.0,
        on_status: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Запустить периодическую эмуляцию RC-команд.

        Args:
            channels: Список значений каналов
            frequency_hz: Частота отправки в Гц
            on_status: Callback для статуса (опционально)
        """
        if self._is_emulating:
            print("Эмуляция уже запущена")
            return

        if not self.transport.is_open:
            self.transport.open()

        self._emulator = CommandEmulator(self.transport)
        self._emulator.start_emulation(channels, frequency_hz)
        self._is_emulating = True
        if on_status:
            on_status("emulation_started")
        print(f"Эмуляция запущена: {len(channels)} каналов, {frequency_hz} Гц")

    def stop_emulation(self) -> None:
        """Остановить эмуляцию."""
        if not self._is_emulating:
            return
        if self._emulator:
            self._emulator.stop_emulation()
            self._emulator = None
        self._is_emulating = False
        print("Эмуляция остановлена")

    def update_channels(self, channels: List[int]) -> None:
        """
        Обновить значения каналов во время эмуляции.

        Args:
            channels: Новые значения каналов
        """
        if self._emulator and self._is_emulating:
            self._emulator.update_channels(channels)

    def is_monitoring(self) -> bool:
        """Проверить, запущен ли мониторинг."""
        return self._is_monitoring

    def is_emulating(self) -> bool:
        """Проверить, запущена ли эмуляция."""
        return self._is_emulating

    def close(self) -> None:
        """Закрыть транспорт и остановить все процессы."""
        self.stop_monitoring()
        self.stop_emulation()
        if self.transport.is_open:
            self.transport.close()