"""
Экран сбора статистики
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label, Input, ProgressBar
from textual.containers import Container, Vertical, Horizontal

import time
import threading

from modem_test_platform.monitoring import RxMonitor, StatCollector, LinkState
from serial_protocol.serial_transport import SerialTransport
from modem_test_platform.tui.widgets.telemetry_table import TelemetryTable
from modem_test_platform.tui.widgets.status_indicator import StatusIndicator


class StatsScreen(Screen):
    """Экран сбора статистики"""

    BINDINGS = [
        ("s", "start", "Старт"),
        ("q", "back", "Назад"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._monitor: RxMonitor = None
        self._transport: SerialTransport = None
        self._collector: StatCollector = None
        self._running = False
        self._start_time = 0.0
        self._duration = 10.0
        self._current_link: LinkState = None

    def compose(self) -> ComposeResult:
        yield Header()

        with Container():
            yield Static("📊 Сбор статистики", classes="panel-title")

            with Horizontal():
                with Vertical(classes="panel"):
                    yield StatusIndicator("Порт", id="port_status")
                    yield StatusIndicator("Сбор", id="collect_status")

                with Vertical(classes="panel"):
                    yield Label("Длительность (сек):")
                    yield Input(value="10", id="duration_input")
                    yield ProgressBar(id="progress_bar", total=100, value=0)

            yield TelemetryTable(id="telemetry_table")

            with Horizontal():
                yield Button("▶ Старт", id="btn_start", variant="primary")
                yield Button("⏹ Стоп", id="btn_stop", variant="error")
                yield Button("💾 Сохранить", id="btn_save", variant="default")
                yield Button("⬅️ Назад", id="btn_back", variant="default")

            yield Static("Нажмите S для старта, Q для выхода", classes="hint")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_start":
            self.action_start()
        elif event.button.id == "btn_stop":
            self.stop_collecting()
        elif event.button.id == "btn_save":
            self.save_stats()
        elif event.button.id == "btn_back":
            self.action_back()

    def action_start(self) -> None:
        self.start_collecting()

    def action_back(self) -> None:
        self.stop_collecting()
        self.app.pop_screen()

    def start_collecting(self) -> None:
        if self._running:
            return

        # Получаем длительность
        duration_input = self.query_one("#duration_input", Input)
        try:
            self._duration = float(duration_input.value)
        except ValueError:
            self._duration = 10.0

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

            self._collector = StatCollector(on_update=self._on_stat_update)
            self._monitor.on_link_state = self._collector.add_sample

            self._monitor.start()
            self._running = True
            self._start_time = time.time()

            self.notify(f"📊 Сбор статистики запущен на {self._duration}с", severity="information")
            self.update_status("collecting")

            # Запускаем таймер обновления прогресса
            def update_progress():
                while self._running:
                    elapsed = time.time() - self._start_time
                    progress = min(100, (elapsed / self._duration) * 100)
                    progress_bar = self.query_one("#progress_bar", ProgressBar)
                    progress_bar.progress = progress

                    if elapsed >= self._duration:
                        break

                    time.sleep(0.1)

            threading.Thread(target=update_progress, daemon=True).start()

            # Автоматическая остановка через duration секунд
            def auto_stop():
                time.sleep(self._duration)
                if self._running:
                    self.stop_collecting()

            threading.Thread(target=auto_stop, daemon=True).start()

        except Exception as e:
            self.notify(f"❌ Ошибка: {e}", severity="error")
            self.update_status("error")

    def stop_collecting(self) -> None:
        if not self._running:
            return

        self._running = False

        if self._monitor:
            self._monitor.stop()
            self._monitor = None

        if self._transport:
            self._transport.close()
            self._transport = None

        self.update_status("done")
        self.notify("⏹ Сбор статистики завершен", severity="information")

        # Показываем итоговую статистику
        if self._collector and not self._collector.is_empty():
            summary = self._collector.get_summary()
            self.notify(summary, severity="information", timeout=10)

    def save_stats(self) -> None:
        """Сохранение статистики в файл"""
        if not self._collector or self._collector.is_empty():
            self.notify("❌ Нет данных для сохранения", severity="error")
            return

        import json
        from datetime import datetime

        stats = self._collector.get_stats()
        filename = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w') as f:
                json.dump(stats, f, indent=2)
            self.notify(f"✅ Статистика сохранена в {filename}", severity="information")
        except Exception as e:
            self.notify(f"❌ Ошибка сохранения: {e}", severity="error")

    def _on_status(self, status: str) -> None:
        """Callback при изменении статуса"""
        self.update_status(status)

    def _on_stat_update(self, collection) -> None:
        """Callback при обновлении статистики"""
        stats = collection.to_dict()

        # Обновляем таблицу с текущими значениями
        if self._current_link:
            table = self.query_one("#telemetry_table", TelemetryTable)
            table.update(
                self._current_link,
                stats['uplink_lq']['count'],
                stats['duration']
            )

    def update_status(self, status: str) -> None:
        """Обновление статуса"""
        port_indicator = self.query_one("#port_status", StatusIndicator)
        port_indicator.status = status

        collect_indicator = self.query_one("#collect_status", StatusIndicator)
        collect_indicator.status = status

    def on_unmount(self) -> None:
        """Очистка при закрытии"""
        self.stop_collecting()