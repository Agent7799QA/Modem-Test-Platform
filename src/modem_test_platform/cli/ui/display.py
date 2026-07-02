"""
Функции для отображения UI-элементов.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import List

from modem_test_platform.devices.modem.adapter.serial_adapter.port_scanner import ModemInfo

console = Console()


def print_header() -> None:
    """Печатает заголовок приложения."""
    console.clear()
    panel = Panel(
        "[bold cyan]📡 MODEM TEST PLATFORM[/bold cyan]\n[white]Интерактивное управление[/white]",
        border_style="cyan",
        box=box.DOUBLE,
        width=80,
    )
    console.print(panel, justify="center")


def display_modems(modems: List[ModemInfo]) -> None:
    """Отобразить список найденных модемов в виде таблицы."""
    if not modems:
        console.print("[red]❌ Модемы не найдены[/red]")
        return

    table = Table(title="📡 Найденные модемы", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=4)
    table.add_column("Порт", style="green", width=12)
    table.add_column("Тип", style="yellow", width=8)

    for i, info in enumerate(modems, 1):
        table.add_row(
            str(i),
            info.port,
            info.port_type,
        )

    console.print(table)


def display_menu_table(state) -> Table:
    """Создать таблицу главного меню."""
    table = Table(box=box.ROUNDED)
    table.add_column("№", style="cyan", width=4)
    table.add_column("Команда", style="white")
    table.add_column("Текущее состояние", style="green", width=40)

    menu_items = [
        ("1", "Перечитать конфигурацию", state.get_config_time_display()),
        ("2", "Чтение состояния канала", state.get_stat_display()),
        ("3", "Установка частоты", state.get_frequency_display()),
        ("4", "Установка режима", state.get_mode_display()),
        ("5", "Установка скорости (rate)", state.get_rate_display()),
        ("6", "Установка протокола", state.get_protocol_display()),
        ("7", "Установка FHSS", state.get_fhss_display()),
        ("8", "Установка DSSS", state.get_dsss_display()),
        ("9", "Установка адреса сети (PAN)", state.get_pan_display()),
        ("10", "Установка адреса управления (BIND)", state.get_bind_display()),
        ("11", "Переключение LED", state.get_led_display()),
        ("12", "Перезагрузка модема", state.get_reboot_display()),
        ("13", "Телеметрия - мониторинг", state.get_monitor_display()),
        ("14", "Телеметрия - сбор статистики", state.get_stats_display()),
        ("15", "Телеметрия - эмуляция команд", state.get_emulation_display()),
        ("16", "Сменить порт", state.port or "—"),
        ("17", "Сканировать порты (TX/RX)", "🔍 Поиск модемов"),
        ("18", "Подключиться к двум модемам", state.get_dual_status()),
        ("19", "Синхронизировать TX→RX", "🔄 Синхронизация"),
        ("20", "Проверить связь", "📡 Пинг модемов"),
        ("21", "Отключить все модемы", "🔴 Отключить"),
        ("0", "Выход", ""),
    ]

    for num, desc, status in menu_items:
        table.add_row(num, desc, status)

    return table