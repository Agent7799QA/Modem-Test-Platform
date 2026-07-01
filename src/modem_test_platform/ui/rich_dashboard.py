"""
Rich-дашборд для отображения телеметрии в реальном времени.
"""

import time
from typing import Optional, Callable

from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console, Group
from rich import box
from rich.text import Text

from modem_test_platform.monitoring.rx_monitor import LinkState
from modem_test_platform.monitoring.stat_collector import StatCollection
from modem_test_platform.ui.rich_utils import (
    create_telemetry_table,
    format_rssi,
    format_lq,
    console,
)


class TelemetryDashboard:
    """
    Интерактивный дашборд для телеметрии.

    Использует Rich Live для обновления в реальном времени.
    """

    def __init__(
            self,
            title: str = "📡 Modem Telemetry Dashboard",
            refresh_rate: float = 0.25,
    ):
        """
        Args:
            title: Заголовок дашборда
            refresh_rate: Частота обновления в секундах
        """
        self.title = title
        self.refresh_rate = refresh_rate
        self._live: Optional[Live] = None
        self._running = False
        self._link: Optional[LinkState] = None
        self._stats: Optional[StatCollection] = None
        self._status: str = "connecting"
        self._on_update: Optional[Callable] = None

    def update(self, link: LinkState, stats: Optional[StatCollection] = None) -> None:
        """
        Обновить данные дашборда.

        Args:
            link: Текущее состояние линка
            stats: Статистика (опционально)
        """
        self._link = link
        self._stats = stats
        self._status = "good"

        if self._live:
            self._live.update(self._create_layout())

    def update_status(self, status: str) -> None:
        """Обновить статус подключения."""
        self._status = status
        if self._live:
            self._live.update(self._create_layout())

    def _create_status_panel(self) -> Panel:
        """Создать панель статуса."""
        status_colors = {
            "good": "green",
            "bad": "red",
            "closed": "grey50",
            "write_error": "orange1",
            "connecting": "yellow",
        }
        status_icons = {
            "good": "✅",
            "bad": "❌",
            "closed": "🔌",
            "write_error": "⚠️",
            "connecting": "🔄",
        }
        color = status_colors.get(self._status, "white")
        icon = status_icons.get(self._status, "❓")

        status_text = Text(f"{icon} {self._status}", style=color)
        return Panel(status_text, title="Статус", border_style=color)

    def _create_stats_summary(self) -> Panel:
        """Создать панель со сводкой статистики."""
        if not self._stats or self._stats.uplink_lq.count == 0:
            return Panel("Нет данных", title="Статистика", border_style="grey50")

        lines = [
            f"Измерений: {self._stats.uplink_lq.count}",
            f"Длительность: {self._stats.duration:.1f}с",
            "",
            f"Uplink LQ:   {self._stats.uplink_lq.min}% / {self._stats.uplink_lq.max}% / {self._stats.uplink_lq.avg:.1f}%",
            f"Uplink RSSI: {self._stats.uplink_rssi.min} / {self._stats.uplink_rssi.max} / {self._stats.uplink_rssi.avg:.1f} dBm",
            f"Downlink LQ: {self._stats.downlink_lq.min}% / {self._stats.downlink_lq.max}% / {self._stats.downlink_lq.avg:.1f}%",
            f"Downlink RSSI: {self._stats.downlink_rssi.min} / {self._stats.downlink_rssi.max} / {self._stats.downlink_rssi.avg:.1f} dBm",
        ]
        content = "\n".join(lines)
        return Panel(content, title="📊 Статистика (мин/макс/сред)", border_style="blue")

    def _create_layout(self) -> Layout:
        """Создать layout дашборда."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        # Заголовок
        header = Panel(
            f"[bold white]{self.title}[/bold white]",
            border_style="cyan",
        )
        layout["header"].update(header)

        # Основная часть
        main_layout = Layout()
        main_layout.split_row(
            Layout(name="telemetry", ratio=2),
            Layout(name="stats", ratio=1),
        )

        # Телеметрия
        if self._link:
            table = create_telemetry_table(self._link, self._stats)
            main_layout["telemetry"].update(table)
        else:
            main_layout["telemetry"].update(Panel("Ожидание данных...", title="Телеметрия"))

        # Статистика
        main_layout["stats"].update(self._create_stats_summary())

        layout["main"].update(main_layout)

        # Футер
        footer = self._create_status_panel()
        layout["footer"].update(footer)

        return layout

    def start(self) -> None:
        """Запустить дашборд."""
        self._running = True
        self._live = Live(
            self._create_layout(),
            console=console,
            refresh_per_second=1.0 / self.refresh_rate,
            screen=True,
        )
        self._live.start()

    def stop(self) -> None:
        """Остановить дашборд."""
        self._running = False
        if self._live:
            self._live.stop()
            self._live = None

    def is_running(self) -> bool:
        """Проверить, запущен ли дашборд."""
        return self._running and self._live is not None


class SimpleMonitorDisplay:
    """
    Простой монитор для отображения телеметрии в одну строку.
    """

    def __init__(self, refresh_rate: float = 0.25):
        self.refresh_rate = refresh_rate
        self._link: Optional[LinkState] = None
        self._stats: Optional[StatCollection] = None
        self._running = False
        self._live: Optional[Live] = None

    def update(self, link: LinkState, stats: Optional[StatCollection] = None) -> None:
        """Обновить отображение."""
        self._link = link
        self._stats = stats

        if self._live:
            self._live.update(self._create_content())

    def _create_content(self) -> Text:
        """Создать содержимое для отображения."""
        if not self._link:
            return Text("Ожидание данных...", style="yellow")

        parts = [
            f"Uplink: LQ={format_lq(self._link.uplink_lq)}, RSSI={format_rssi(self._link.uplink_rssi)}",
            f"Downlink: LQ={format_lq(self._link.downlink_lq)}, RSSI={format_rssi(self._link.downlink_rssi)}",
        ]

        if self._stats and self._stats.uplink_lq.count > 0:
            parts.append(f"📊 Измерений: {self._stats.uplink_lq.count}, {self._stats.duration:.1f}с")

        return Text(" | ").join(parts)

    def start(self) -> None:
        """Запустить отображение."""
        self._running = True
        self._live = Live(
            self._create_content(),
            console=console,
            refresh_per_second=1.0 / self.refresh_rate,
        )
        self._live.start()

    def stop(self) -> None:
        """Остановить отображение."""
        self._running = False
        if self._live:
            self._live.stop()
            self._live = None