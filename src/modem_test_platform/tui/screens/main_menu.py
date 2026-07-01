"""
Экран главного меню
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label
from textual.containers import Container, Horizontal, Vertical

from modem_test_platform.tui.screens.config_screen import ConfigScreen
from modem_test_platform.tui.screens.monitor_screen import MonitorScreen
from modem_test_platform.tui.screens.stats_screen import StatsScreen
from modem_test_platform.tui.screens.emulation_screen import EmulationScreen


class MainMenu(Screen):
    """Главное меню приложения"""

    BINDINGS = [
        ("1", "go_to_configure", "Проверка подключения"),
        ("2", "go_to_read_config", "Чтение конфигурации"),
        ("3", "go_to_read_stat", "Состояние канала"),
        ("4", "go_to_set_frequency", "Установка частоты"),
        ("5", "go_to_set_mode", "Установка режима"),
        ("6", "go_to_toggle_led", "Переключение LED"),
        ("7", "go_to_reboot", "Перезагрузка"),
        ("8", "go_to_monitor", "Мониторинг телеметрии"),
        ("9", "go_to_stats", "Сбор статистики"),
        ("0", "go_to_emulation", "Эмуляция команд"),
        ("q", "quit", "Выход"),
    ]

    def compose(self) -> ComposeResult:
        """Создание интерфейса"""
        yield Header()

        with Vertical(id="menu-container"):
            yield Static("📡 MODEM TEST PLATFORM", classes="header")
            yield Static("Главное меню", classes="panel-title")

            with Container(classes="menu-grid"):
                with Horizontal():
                    with Vertical(classes="menu-column"):
                        yield Button("🔧 1. Проверка подключения", id="btn_configure", variant="default")
                        yield Button("📖 2. Чтение конфигурации", id="btn_read_config", variant="default")
                        yield Button("📊 3. Состояние канала", id="btn_read_stat", variant="default")
                        yield Button("📡 4. Установка частоты", id="btn_set_frequency", variant="default")
                        yield Button("🔧 5. Установка режима", id="btn_set_mode", variant="default")
                        yield Button("💡 6. Переключение LED", id="btn_toggle_led", variant="default")
                    with Vertical(classes="menu-column"):
                        yield Button("🔄 7. Перезагрузка модема", id="btn_reboot", variant="default")
                        yield Button("📡 8. Мониторинг телеметрии", id="btn_monitor", variant="default")
                        yield Button("📊 9. Сбор статистики", id="btn_stats", variant="default")
                        yield Button("🎮 0. Эмуляция команд", id="btn_emulation", variant="default")
                        yield Button("🔌 Сменить порт", id="btn_change_port", variant="default")
                        yield Button("🚪 Выход", id="btn_exit", variant="error")

            yield Static("Нажмите букву команды (1-9, 0) или q для выхода", classes="hint")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Обработка нажатия кнопок"""
        button_id = event.button.id

        if button_id == "btn_configure":
            self.app.push_screen("configure")
        elif button_id == "btn_read_config":
            self.app.push_screen("read_config")
        elif button_id == "btn_read_stat":
            self.app.push_screen("read_stat")
        elif button_id == "btn_set_frequency":
            self.app.push_screen("set_frequency")
        elif button_id == "btn_set_mode":
            self.app.push_screen("set_mode")
        elif button_id == "btn_toggle_led":
            self.app.push_screen("toggle_led")
        elif button_id == "btn_reboot":
            self.app.push_screen("reboot")
        elif button_id == "btn_monitor":
            self.app.push_screen("monitor")
        elif button_id == "btn_stats":
            self.app.push_screen("stats")
        elif button_id == "btn_emulation":
            self.app.push_screen("emulation")
        elif button_id == "btn_change_port":
            self.app.push_screen("config")
        elif button_id == "btn_exit":
            self.app.exit()

    def action_go_to_configure(self) -> None:
        self.app.push_screen("configure")

    def action_go_to_read_config(self) -> None:
        self.app.push_screen("read_config")

    def action_go_to_read_stat(self) -> None:
        self.app.push_screen("read_stat")

    def action_go_to_set_frequency(self) -> None:
        self.app.push_screen("set_frequency")

    def action_go_to_set_mode(self) -> None:
        self.app.push_screen("set_mode")

    def action_go_to_toggle_led(self) -> None:
        self.app.push_screen("toggle_led")

    def action_go_to_reboot(self) -> None:
        self.app.push_screen("reboot")

    def action_go_to_monitor(self) -> None:
        self.app.push_screen("monitor")

    def action_go_to_stats(self) -> None:
        self.app.push_screen("stats")

    def action_go_to_emulation(self) -> None:
        self.app.push_screen("emulation")