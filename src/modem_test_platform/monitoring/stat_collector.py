"""
Сбор и анализ статистики по сигналам из CRSF-телеметрии.
Адаптирован из старого stat_collector.py (убраны Qt-зависимости).
"""

import time
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from collections import defaultdict

from modem_test_platform.monitoring.rx_monitor import LinkState


@dataclass
class StatData:
    """Статистика по одному параметру."""
    values: List[float] = field(default_factory=list)
    min: Optional[float] = None
    max: Optional[float] = None
    avg: Optional[float] = None
    count: int = 0

    def update(self, value: float) -> None:
        """Обновить статистику новым значением."""
        self.values.append(value)
        self.count += 1

        if self.min is None or value < self.min:
            self.min = value
        if self.max is None or value > self.max:
            self.max = value

        # Пересчет среднего
        total = sum(self.values)
        self.avg = total / self.count if self.count > 0 else 0

    def clear(self) -> None:
        """Очистить статистику."""
        self.values.clear()
        self.min = None
        self.max = None
        self.avg = None
        self.count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            "min": self.min,
            "max": self.max,
            "avg": self.avg,
            "count": self.count,
        }


@dataclass
class StatCollection:
    """Сбор статистики по всем параметрам."""

    # Основные параметры
    uplink_lq: StatData = field(default_factory=StatData)
    uplink_rssi: StatData = field(default_factory=StatData)
    downlink_lq: StatData = field(default_factory=StatData)
    downlink_rssi: StatData = field(default_factory=StatData)

    # Время сбора
    start_time: Optional[float] = None
    last_update_time: Optional[float] = None
    duration: float = 0.0  # секунд

    def add_sample(self, link_state: LinkState) -> None:
        """Добавить одно измерение."""
        if self.start_time is None:
            self.start_time = time.time()

        self.uplink_lq.update(link_state.uplink_lq)
        self.uplink_rssi.update(link_state.uplink_rssi)
        self.downlink_lq.update(link_state.downlink_lq)
        self.downlink_rssi.update(link_state.downlink_rssi)

        self.last_update_time = time.time()
        self.duration = self.last_update_time - self.start_time

    def clear(self) -> None:
        """Очистить все данные."""
        self.uplink_lq.clear()
        self.uplink_rssi.clear()
        self.downlink_lq.clear()
        self.downlink_rssi.clear()
        self.start_time = None
        self.last_update_time = None
        self.duration = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            "uplink_lq": self.uplink_lq.to_dict(),
            "uplink_rssi": self.uplink_rssi.to_dict(),
            "downlink_lq": self.downlink_lq.to_dict(),
            "downlink_rssi": self.downlink_rssi.to_dict(),
            "duration": self.duration,
            "start_time": self.start_time,
            "last_update_time": self.last_update_time,
        }

    def is_empty(self) -> bool:
        """Проверить, есть ли данные."""
        return self.uplink_lq.count == 0

    def get_summary(self) -> str:
        """Получить краткое резюме."""
        if self.is_empty():
            return "Нет данных"

        return (
            f"Собрано {self.uplink_lq.count} измерений за {self.duration:.1f}с\n"
            f"Uplink LQ:   min={self.uplink_lq.min}%, max={self.uplink_lq.max}%, avg={self.uplink_lq.avg:.1f}%\n"
            f"Uplink RSSI: min={self.uplink_rssi.min} dBm, max={self.uplink_rssi.max} dBm, avg={self.uplink_rssi.avg:.1f} dBm\n"
            f"Downlink LQ: min={self.downlink_lq.min}%, max={self.downlink_lq.max}%, avg={self.downlink_lq.avg:.1f}%\n"
            f"Downlink RSSI: min={self.downlink_rssi.min} dBm, max={self.downlink_rssi.max} dBm, avg={self.downlink_rssi.avg:.1f} dBm"
        )


class StatCollector:
    """
    Сбор статистики по сигналам из CRSF-телеметрии.

    Подписывается на обновления LinkState, собирает статистику
    и вызывает callback при каждом обновлении.

    Адаптирован из старого Statistic_Collector.
    """

    def __init__(
            self,
            on_update: Optional[Callable[[StatCollection], None]] = None,
            on_clear: Optional[Callable[[], None]] = None,
    ):
        """
        Args:
            on_update: Callback при обновлении статистики
            on_clear: Callback при очистке статистики
        """
        self.on_update = on_update
        self.on_clear = on_clear
        self._collection = StatCollection()
        self._lock = threading.Lock()
        self._running = False

    def add_sample(self, link_state: LinkState) -> None:
        """
        Добавить новое измерение.

        Args:
            link_state: Состояние линка (LQ, RSSI)
        """
        with self._lock:
            self._collection.add_sample(link_state)

        # Вызываем callback
        if self.on_update:
            self.on_update(self._collection)

    def get_collection(self) -> StatCollection:
        """Получить текущую коллекцию статистики."""
        with self._lock:
            return self._collection

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику в виде словаря."""
        with self._lock:
            return self._collection.to_dict()

    def clear(self) -> None:
        """Очистить собранную статистику."""
        with self._lock:
            self._collection.clear()

        if self.on_clear:
            self.on_clear()

    def is_empty(self) -> bool:
        """Проверить, есть ли данные."""
        with self._lock:
            return self._collection.is_empty()

    def get_summary(self) -> str:
        """Получить краткое резюме."""
        with self._lock:
            return self._collection.get_summary()

    def start(self) -> None:
        """Запустить сбор (для совместимости)."""
        self._running = True
        print("StatCollector started")

    def stop(self) -> None:
        """Остановить сбор (для совместимости)."""
        self._running = False
        print("StatCollector stopped")

    def is_running(self) -> bool:
        """Проверить, запущен ли сбор."""
        return self._running


class StatCollectorThread(StatCollector):
    """
    Версия StatCollector в отдельном потоке.

    Запускает фоновый поток для периодического обновления статистики.
    """

    def __init__(
            self,
            monitor: 'RxMonitor',
            on_update: Optional[Callable[[StatCollection], None]] = None,
            on_clear: Optional[Callable[[], None]] = None,
    ):
        super().__init__(on_update, on_clear)
        self.monitor = monitor
        self._thread: Optional[threading.Thread] = None

        # Подписываемся на обновления LinkState
        self.monitor.on_link_state = self._on_link_state

    def _on_link_state(self, link_state: LinkState) -> None:
        """Callback при получении нового LinkState."""
        self.add_sample(link_state)

    def start(self) -> None:
        """Запустить сбор в отдельном потоке."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("StatCollectorThread started")

    def _run(self) -> None:
        """Фоновый цикл."""
        while self._running:
            time.sleep(0.1)

    def stop(self) -> None:
        """Остановить сбор."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            self._thread = None
        print("StatCollectorThread stopped")

    def clear(self) -> None:
        """Очистить статистику."""
        super().clear()
        # Также очищаем историю в мониторе если нужно
        if hasattr(self.monitor, 'reset_stats'):
            self.monitor.reset_stats()