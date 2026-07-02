"""
Обработчики команд управления устройством.
"""

import logging
from datetime import datetime

from rich.prompt import Confirm

from modem_test_platform.cli.commands import (
    get_modem,
    read_config_cmd,
    read_stat_cmd,
)
from modem_test_platform.cli.session import create_args, execute_command_with_state, state
from modem_test_platform.cli.ui.prompts import select_modem_interactive, select_port_manually
from modem_test_platform.cli.ui.display import console

logger = logging.getLogger(__name__)


def handle_read_config(port: str) -> int:
    """Перечитать конфигурацию (только print, без stat)."""
    global state
    console.print("[bold blue]📖 Перечитывание конфигурации...[/bold blue]")

    try:
        if state.modem is None:
            state.modem = get_modem(port, timeout=0.5)
            state.port = port
            state.modem.connect()
            console.print(f"[green]✅ Подключено к модему на порту {port}[/green]")
        elif not state.modem.protocol.transport.is_open:
            state.modem.connect()
            console.print(f"[green]✅ Подключено к модему на порту {port}[/green]")

        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
            console.print("[green]✅ Конфигурация получена[/green]")
            state.last_command_time = datetime.now().strftime("%H:%M:%S")
            return 0
        else:
            console.print("[red]❌ Не удалось получить конфигурацию[/red]")
            return 1

    except Exception as e:
        console.print(f"[red]❌ Ошибка: {e}[/red]")
        logger.exception("Ошибка при чтении конфигурации")
        return 1


def handle_read_stat(port: str) -> int:
    """Чтение состояния канала."""
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    args = create_args(port)

    def update():
        link_state = state.modem.read_link_state()
        if link_state:
            state.update_from_link_state(link_state)

    return execute_command_with_state(
        read_stat_cmd, args, "📊 Чтение состояния канала", update
    )


def handle_change_port(port: str):
    """Сменить порт."""
    global state
    if state.modem is not None:
        try:
            state.modem.disconnect()
        except:
            pass
        state.modem = None
        state.is_connected = False

    # Сканируем порты заново
    from modem_test_platform.devices.modem.adapter.serial_adapter.port_scanner import scan_ports
    modems = scan_ports(timeout=0.5)

    if modems:
        new_port = select_modem_interactive(modems)
    else:
        console.print("[yellow]⚠️ Модемы не найдены. Выберите порт вручную.[/yellow]")
        new_port = select_port_manually()

    if new_port:
        console.print(f"[green]✅ Выбран порт: {new_port}[/green]")
        return new_port
    return None


def handle_exit(port: str) -> int:
    """Выход из программы."""
    global state
    if state.modem is not None:
        try:
            state.modem.disconnect()
            console.print("[green]✅ Модем отключен[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Ошибка при отключении: {e}[/yellow]")
    console.print("\n[bold green]👋 До свидания![/bold green]")
    return 0


def handle_connect_modem(port: str) -> bool:
    """Подключение к модему (вспомогательная функция)."""
    global state
    try:
        state.modem = get_modem(port, timeout=0.5)
        state.modem.connect()
        console.print(f"[green]✅ Подключено к модему на порту {port}[/green]")

        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
            console.print("[green]✅ Конфигурация загружена[/green]")
            state.last_command_time = datetime.now().strftime("%H:%M:%S")
            return True
        else:
            console.print("[yellow]⚠️ Не удалось загрузить конфигурацию[/yellow]")
            console.print("[yellow]   Возможно, это порт данных (скорость 420000 бод).[/yellow]")
            console.print("[yellow]   Для управления модемом используйте порт конфигурации (115200 бод).[/yellow]")
            return False
    except Exception as e:
        console.print(f"[red]❌ Ошибка при подключении: {e}[/red]")
        console.print("[yellow]⚠️ Некоторые команды могут быть недоступны.[/yellow]")
        console.print("[yellow]   Проверьте, что вы подключились к порту конфигурации (115200 бод).[/yellow]")
        return False