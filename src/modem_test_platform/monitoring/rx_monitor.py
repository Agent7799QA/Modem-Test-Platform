"""
Мониторинг RX порта данных с парсингом CRSF протокола.
Адаптирован из старого rx_parser.py (убраны Qt-зависимости).
"""
import logging
from typing import Callable, Optional, Container, Dict, Any
from dataclasses import dataclass

from modem_test_platform.monitoring.base_monitor import BaseMonitor, MonitorConfig
from modem_test_platform.protocols.crossfire.crsf_parser import (
    CRSFParser,
    PacketValidationStatus,
    PacketsTypes,
)
logger = logging.getLogger(__name__)

@dataclass
class LinkState:
    """Состояние линка (LQ и RSSI)."""
    uplink_lq: int = 0
    uplink_rssi: int = 0
    downlink_lq: int = 0
    downlink_rssi: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uplink_lq": self.uplink_lq,
            "uplink_rssi": self.uplink_rssi,
            "downlink_lq": self.downlink_lq,
            "downlink_rssi": self.downlink_rssi,
        }

    def __str__(self) -> str:
        return (
            f"Uplink LQ: {self.uplink_lq}%, RSSI: {self.uplink_rssi} dBm, "
            f"Downlink LQ: {self.downlink_lq}%, RSSI: {self.downlink_rssi} dBm"
        )


@dataclass
class RxMonitorStats:
    """Статистика работы монитора."""
    valid_frames: int = 0
    invalid_frames: int = 0
    crc_errors: int = 0
    framing_errors: int = 0
    link_statistics_frames: int = 0


class RxMonitor:
    """
    Мониторинг RX порта с парсингом CRSF.

    Читает данные с порта данных (420000 бод),
    парсит CRSF-пакеты и вызывает callback'и.

    Адаптирован из RxParsingThread старого стенда.
    """

    def __init__(
            self,
            port_name: Optional[str] = None,
            monitor: Optional[BaseMonitor] = None,   # <-- НОВЫЙ ПАРАМЕТР
            on_link_state: Callable[[LinkState], None] = None,
            on_frame: Callable[[Container, PacketValidationStatus], None] = None,
            on_status: Callable[[str], None] = None,
            config: MonitorConfig = None,
    ):
        """
        Args:
            port_name: Имя COM-порта (если monitor не передан)
            monitor: Внешний экземпляр BaseMonitor (если передан, port_name игнорируется)
            on_link_state: Callback при получении LINK_STATISTICS (LinkState)
            on_frame: Callback при любом валидном фрейме (frame, status)
            on_status: Callback при изменении статуса порта
            config: Конфигурация монитора
        """
        self.on_link_state = on_link_state
        self.on_frame = on_frame
        self.on_status = on_status

        # Создаем CRSF парсер с callback
        self._parser = CRSFParser(self._on_parsed_frame)

        # Если передан внешний монитор, используем его
        if monitor is not None:
            self._monitor = monitor
            # Если задан port_name, но передан monitor, игнорируем port_name
        else:
            # Создаем свой монитор
            self._monitor = BaseMonitor(
                port_name=port_name,
                on_data=self._on_data_received,
                on_status=on_status,
                config=config or MonitorConfig(baudrate=420000),
            )

        # Статистика
        self._stats = RxMonitorStats()

    def _on_data_received(self, data: bytes) -> None:
        """Callback при получении данных из порта."""
        input_data = bytearray(data)
        try:
            self._parser.parse_stream(input_data)
        except KeyError as e:
            if 'frame_length' in str(e):
                print(f"Невалидный CRSF пакет: {input_data}")
            else:
                print(f"Ошибка парсинга: {e}")
        except Exception as e:
            print(f"Общая ошибка парсинга: {e}")

    def _on_parsed_frame(self, frame: Container, status: PacketValidationStatus) -> None:
        """Callback при распарсенном CRSF-фрейме."""
        # Обновляем статистику
        if status == PacketValidationStatus.VALID:
            self._stats.valid_frames += 1
        elif status == PacketValidationStatus.CRC:
            self._stats.crc_errors += 1
        elif status == PacketValidationStatus.INVALID:
            self._stats.invalid_frames += 1

        # Вызываем общий callback
        if self.on_frame:
            self.on_frame(frame, status)

        # Обрабатываем только валидные фреймы
        if status != PacketValidationStatus.VALID:
            return

        # Извлекаем тип пакета
        try:
            packet_type = frame.header.type
        except AttributeError:
            return

        # Обрабатываем LINK_STATISTICS
        if packet_type == PacketsTypes.LINK_STATISTICS:
            self._stats.link_statistics_frames += 1
            try:
                payload = frame.payload
                link_state = LinkState(
                    uplink_lq=payload.uplink_link_quality,
                    uplink_rssi=payload.uplink_rssi_ant_1,
                    downlink_lq=payload.downlink_link_quality,
                    downlink_rssi=payload.downlink_rssi,
                )
                if self.on_link_state:
                    self.on_link_state(link_state)
            except Exception as e:
                print(f"Error parsing LINK_STATISTICS: {e}")

        # Обрабатываем LINK_STATISTICS_EXTENDED
        elif packet_type == PacketsTypes.LINK_STATISTICS_EXTENDED:
            self._stats.link_statistics_frames += 1
            try:
                payload = frame.payload
                link_state = LinkState(
                    uplink_lq=payload.uplink_link_quality,
                    uplink_rssi=payload.uplink_rssi_ant_1,
                    downlink_lq=payload.downlink_link_quality,
                    downlink_rssi=payload.downlink_rssi,
                )
                if self.on_link_state:
                    self.on_link_state(link_state)
            except Exception as e:
                print(f"Error parsing LINK_STATISTICS_EXTENDED: {e}")

    # ========== Прокси-методы ==========

    def set_transport(self, transport) -> None:
        """Установить внешний транспорт для монитора."""
        self._monitor.set_transport(transport)

    def set_port(self, port_name: str) -> None:
        """Установить порт для мониторинга."""
        self._monitor.set_port(port_name)

    def start(self) -> None:
        """Запустить мониторинг."""
        self._monitor.start()

    def stop(self) -> None:
        """Остановить мониторинг."""
        self._monitor.stop()

    def is_running(self) -> bool:
        """Проверить, запущен ли мониторинг."""
        return self._monitor.is_running()

    def is_port_open(self) -> bool:
        """Проверить, открыт ли порт."""
        return self._monitor.is_port_open()

    def write(self, data: bytes) -> int:
        """Написать данные в порт (для эмуляции)."""
        return self._monitor.write(data)

    def start_writing(self, command: bytes, frequency_hz: float = 1.0) -> None:
        """Начать периодическую запись команды."""
        self._monitor.start_writing(command, frequency_hz)

    def stop_writing(self) -> None:
        """Остановить периодическую запись."""
        self._monitor.stop_writing()

    def get_stats(self) -> RxMonitorStats:
        """Получить статистику работы монитора."""
        return self._stats

    def reset_stats(self) -> None:
        """Сбросить статистику."""
        self._stats = RxMonitorStats()