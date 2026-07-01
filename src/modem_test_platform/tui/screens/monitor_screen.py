"""
Экран мониторинга телеметрии
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label, Input
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from rich.text import Text

import time
import threading

from modem_test_platform.monitoring import RxMonitor, LinkState
from modem_test_platform.transport.serial.serial_transport import SerialTransport
from modem_test_platform.tui.widgets.telemetry_table import TelemetryTable
from modem_test_platform.tui.widgets.status_indicator import StatusIndicator


class MonitorScreen(Screen):
    """Экран мониторинга телеметрии в реальном времени"""

    BINDINGS = [
        ("s", "toggle", "Старт/Стоп"),
        ("q", "back", "Назад"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._monitor: RxMonitor = None
        self._transport: SerialTransport = None
        self._running = False
        self._count = 0
        self._start_time = 0.0
        self._link: LinkState = None

    def compose(self) -> ComposeResult:
        yield Header()

        with Container():
            yield Static("📡 Мониторинг телеметрии", classes="panel-title")

            with Horizontal():
                with Vertical(classes="panel"):
                    yield StatusIndicator("Порт", id="port_status")
                    yield StatusIndicator("Соединение", id="conn_status")

                with Vertical(classes="panel"):
                    yield Label("Интервал обновления (сек):")
                    yield Input(value="0.25", id="interval_input")
                    yield Horizontal(
                        Button("▶ Старт", id="btn_start", variant="primary"),
                        Button("⏹ Стоп", id="btn_stop", variant="error"),
                    )

            yield TelemetryTable(id="telemetry_table")

            yield Static("Нажмите S для старта/стопа, Q для выхода", classes="hint")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_start":
            self.start_monitoring()
        elif event.button.id == "btn_stop":
            self.stop_monitoring()

    def action_toggle(self) -> None:
        if self._running:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def action_back(self) -> None:
        self.stop_monitoring()
        self.app.pop_screen()

    def start_monitoring(self) -> None:
        if self._running:
            return

        # Получаем интервал
        interval_input = self.query_one("#interval_input", Input)
        try:
            interval = float(interval_input.value)
        except ValueError:
            interval = 0.25

        # Проверяем порт
        if not hasattr(self.app, 'port') or not self.app.port:
            self.notify("❌ Порт не выбран", severity="error")
            return

        try:
            # Создаем транспорт и монитор
            self._transport = SerialTransport(
                port=self.app.port,
                baudrate=420000,
                timeout=0.1,
            )
            self._transport.open()

            self._monitor = RxMonitor(
                port_name=self.app.port,
                on_status=self._on_status,
            )
            self._monitor._monitor._serial_port = self._transport._serial
            self._monitor.on_link_state = self._on_link_state

            self._monitor.start()
            self._running = True
            self._start_time = time.time()
            self._count = 0

            self.notify(f"✅ Мониторинг запущен на порту {self.app.port}", severity="information")
            self.update_status("connected")

        except Exception as e:
            self.notify(f"❌ Ошибка: {e}", severity="error")
            self.update_status("error")

    def stop_monitoring(self) -> None:
        if not self._running:
            return

        self._running = False

        if self._monitor:
            self._monitor.stop()
            self._monitor = None

        if self._transport:
            self._transport.close()
            self._transport = None

        self.update_status("disconnected")
        self.notify("⏹ Мониторинг остановлен", severity="information")

    def _on_status(self, status: str) -> None:
        """Callback при изменении статуса"""
        self.update_status(status)

    def _on_link_state(self, link: LinkState) -> None:
        """Callback при получении данных"""
        self._link = link
        self._count += 1
        duration = time.time() - self._start_time

        # Обновляем таблицу
        table = self.query_one("#telemetry_table", TelemetryTable)
        table.update(link, self._count, duration)

    def update_status(self, status: str) -> None:
        """Обновление статуса"""
        port_indicator = self.query_one("#port_status", StatusIndicator)
        port_indicator.status = status

        conn_indicator = self.query_one("#conn_status", StatusIndicator)
        conn_indicator.status = status

    def on_unmount(self) -> None:
        """Очистка при закрытии"""
        self.stop_monitoring()