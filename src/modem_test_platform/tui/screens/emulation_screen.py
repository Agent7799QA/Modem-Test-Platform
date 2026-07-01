"""
Экран эмуляции команд
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label, Input, TextArea
from textual.containers import Container, Vertical, Horizontal

import threading
import time

from modem_test_platform.transport.serial.serial_transport import SerialTransport
from modem_test_platform.emulation import CommandEmulator
from modem_test_platform.cli.commands.telemetry_commands import parse_channels


class EmulationScreen(Screen):
    """Экран эмуляции команд"""

    BINDINGS = [
        ("e", "emulate", "Эмулировать"),
        ("s", "stop", "Стоп"),
        ("q", "back", "Назад"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._emulator: CommandEmulator = None
        self._transport: SerialTransport = None
        self._running = False
        self._command_count = 0

    def compose(self) -> ComposeResult:
        yield Header()

        with Container():
            yield Static("🎮 Эмуляция команд", classes="panel-title")

            with Horizontal():
                with Vertical(classes="panel"):
                    yield Label("Каналы (через запятую):")
                    yield TextArea(
                        "1500,1500,1500,1500,1000,2000,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500",
                        id="channels_input",
                        classes="channels-area",
                    )

                with Vertical(classes="panel"):
                    yield Label("Частота (Гц):")
                    yield Input(value="10", id="frequency_input")
                    yield Label("Статус:", id="status_label")
                    yield Static("⭕ Готов", id="status_indicator")
                    yield Label(f"Отправлено: {self._command_count}", id="count_label")

            with Horizontal():
                yield Button("▶ Эмулировать", id="btn_emulate", variant="primary")
                yield Button("⏹ Стоп", id="btn_stop", variant="error")
                yield Button("📤 Отправить один раз", id="btn_once", variant="default")
                yield Button("⬅️ Назад", id="btn_back", variant="default")

            yield Static("Нажмите E для эмуляции, S для стопа, Q для выхода", classes="hint")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_emulate":
            self.action_emulate()
        elif event.button.id == "btn_stop":
            self.action_stop()
        elif event.button.id == "btn_once":
            self.send_once()
        elif event.button.id == "btn_back":
            self.action_back()

    def action_emulate(self) -> None:
        self.start_emulation()

    def action_stop(self) -> None:
        self.stop_emulation()

    def action_back(self) -> None:
        self.stop_emulation()
        self.app.pop_screen()

    def start_emulation(self) -> None:
        if self._running:
            return

        # Получаем каналы
        channels_input = self.query_one("#channels_input", TextArea)
        channels_str = channels_input.text.strip()
        channels = parse_channels(channels_str)

        if not channels:
            self.notify("❌ Неверные каналы", severity="error")
            return

        # Получаем частоту
        freq_input = self.query_one("#frequency_input", Input)
        try:
            frequency = float(freq_input.value)
        except ValueError:
            frequency = 10.0

        # Проверяем порт
        if not hasattr(self.app, 'port') or not self.app.port:
            self.notify("❌ Порт не выбран", severity="error")
            return

        try:
            self._transport = SerialTransport(
                port=self.app.port,
                baudrate=420000,
                timeout=0.1,
            )
            self._transport.open()

            self._emulator = CommandEmulator(self._transport)
            self._emulator.start_emulation(channels, frequency)

            self._running = True
            self._command_count = 0

            self.update_status("▶️ Эмуляция запущена", "good")
            self.notify(f"✅ Эмуляция запущена на {frequency} Гц", severity="information")

            # Запускаем счетчик
            def update_count():
                while self._running:
                    time.sleep(0.5)
                    if self._emulator:
                        self._command_count = self._emulator.get_command_count()
                        count_label = self.query_one("#count_label", Label)
                        count_label.update(f"Отправлено: {self._command_count}")

            threading.Thread(target=update_count, daemon=True).start()

        except Exception as e:
            self.notify(f"❌ Ошибка: {e}", severity="error")
            self.update_status("❌ Ошибка", "error")

    def stop_emulation(self) -> None:
        if not self._running:
            return

        self._running = False

        if self._emulator:
            self._emulator.stop_emulation()
            self._emulator = None

        if self._transport:
            self._transport.close()
            self._transport = None

        self.update_status("⭕ Остановлено", "disconnected")
        self.notify("⏹ Эмуляция остановлена", severity="information")

    def send_once(self) -> None:
        """Отправить команды один раз"""
        # Получаем каналы
        channels_input = self.query_one("#channels_input", TextArea)
        channels_str = channels_input.text.strip()
        channels = parse_channels(channels_str)

        if not channels:
            self.notify("❌ Неверные каналы", severity="error")
            return

        # Проверяем порт
        if not hasattr(self.app, 'port') or not self.app.port:
            self.notify("❌ Порт не выбран", severity="error")
            return

        try:
            transport = SerialTransport(port=self.app.port, baudrate=420000)
            transport.open()

            emulator = CommandEmulator(transport)
            emulator.send_once(channels)

            self.notify(f"✅ Отправлено {len(channels)} каналов", severity="information")
            self._command_count += 1
            count_label = self.query_one("#count_label", Label)
            count_label.update(f"Отправлено: {self._command_count}")

            transport.close()

        except Exception as e:
            self.notify(f"❌ Ошибка: {e}", severity="error")

    def update_status(self, text: str, style: str = "disconnected") -> None:
        """Обновление статуса"""
        indicator = self.query_one("#status_indicator", Static)
        indicator.update(text)
        indicator.set_class(style, True)

        # Убираем другие классы
        for cls in ["good", "bad", "warning", "disconnected"]:
            if cls != style:
                indicator.remove_class(cls)