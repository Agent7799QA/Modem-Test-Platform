"""
Экран настройки порта
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Label
from textual.containers import Container, Vertical, Horizontal

import serial.tools.list_ports


class ConfigScreen(Screen):
    """Экран настройки порта"""

    def compose(self) -> ComposeResult:
        yield Header()

        with Container():
            yield Static("🔌 Настройка порта", classes="panel-title")

            # Список портов
            ports = [p.device for p in serial.tools.list_ports.comports()]

            if ports:
                port_list = "\n".join([f"  {i + 1}. {p}" for i, p in enumerate(ports)])
                yield Static(f"Доступные порты:\n{port_list}", classes="panel")
                yield Label("Введите номер порта или название:")
                yield Input(placeholder="Например: COM8 или 1", id="port_input")
            else:
                yield Static("⚠️ COM-порты не найдены", classes="panel error")
                yield Button("Обновить", id="btn_refresh", variant="default")

            yield Horizontal(
                Button("✅ Подключить", id="btn_connect", variant="primary"),
                Button("⬅️ Назад", id="btn_back", variant="default"),
            )

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_connect":
            port_input = self.query_one("#port_input", Input).value.strip()
            if port_input:
                # Проверяем, может быть это номер
                try:
                    idx = int(port_input) - 1
                    ports = [p.device for p in serial.tools.list_ports.comports()]
                    if 0 <= idx < len(ports):
                        self.app.port = ports[idx]
                        self.notify(f"✅ Порт {self.app.port} выбран", severity="information")
                        self.app.pop_screen()
                        return
                except ValueError:
                    pass

                # Иначе считаем, что это название порта
                self.app.port = port_input
                self.notify(f"✅ Порт {self.app.port} выбран", severity="information")
                self.app.pop_screen()
            else:
                self.notify("❌ Введите порт", severity="error")

        elif event.button.id == "btn_back":
            self.app.pop_screen()

        elif event.button.id == "btn_refresh":
            self.refresh()