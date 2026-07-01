"""
Главное приложение Textual
"""

from textual.app import App
from textual.binding import Binding

from modem_test_platform.tui.screens.main_menu import MainMenu
from modem_test_platform.tui.screens.config_screen import ConfigScreen
from modem_test_platform.tui.screens.monitor_screen import MonitorScreen
from modem_test_platform.tui.screens.stats_screen import StatsScreen
from modem_test_platform.tui.screens.emulation_screen import EmulationScreen


class ModemTestApp(App):
    """Главное приложение Modem Test Platform"""

    CSS_PATH = "styles/main.tcss"
    BINDINGS = [
        Binding("ctrl+c", "quit", "Выход"),
    ]

    def __init__(self):
        super().__init__()
        self.port = None

    def on_mount(self) -> None:
        """Инициализация приложения"""
        self.title = "Modem Test Platform"
        self.sub_title = "Интерактивное управление модемом"

        # Регистрируем экраны
        self.install_screen(MainMenu(), "main")
        self.install_screen(ConfigScreen(), "config")
        self.install_screen(MonitorScreen(), "monitor")
        self.install_screen(StatsScreen(), "stats")
        self.install_screen(EmulationScreen(), "emulation")

        # Запускаем с главного меню
        self.push_screen("main")

    def action_quit(self) -> None:
        """Выход из приложения"""
        self.exit()


def run_app():
    """Запуск приложения"""
    app = ModemTestApp()
    app.run()


if __name__ == "__main__":
    run_app()