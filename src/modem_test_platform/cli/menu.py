"""
Главное меню и цикл приложения.
"""

import sys
import logging
from datetime import datetime

from rich.prompt import Prompt
from rich import box

from modem_test_platform.cli.commands import (
    cmd_scan_ports,
    cmd_connect_dual,
    cmd_sync_modems,
    cmd_verify_link,
    cmd_disconnect_dual,
)
from modem_test_platform.devices.modem.adapter.serial_adapter.port_scanner import scan_ports
from modem_test_platform.cli.session import state
from modem_test_platform.cli.ui.display import print_header, display_menu_table, console
from modem_test_platform.cli.ui.prompts import select_modem_interactive, select_port_manually
from modem_test_platform.cli.handlers.device_handlers import (
    handle_read_config,
    handle_read_stat,
    handle_change_port,
    handle_exit,
    handle_connect_modem,
)
from modem_test_platform.cli.handlers.config_handlers import (
    handle_set_frequency,
    handle_set_mode,
    handle_set_rate,
    handle_set_protocol,
    handle_set_fhss,
    handle_set_dsss,
    handle_set_pan,
    handle_set_bind,
    handle_toggle_led,
    handle_reboot,
)
from modem_test_platform.cli.handlers.telemetry_handlers import (
    handle_telemetry_monitor,
    handle_telemetry_collect,
    handle_telemetry_emulate,
)

logger = logging.getLogger(__name__)


def run():
    """Главный цикл приложения."""
    global state

    try:
        # 1. Сканируем порты
        console.print("\n[bold blue]🔍 Сканирование портов...[/bold blue]")
        logger.info("Начало сканирования портов")

        modems = scan_ports(timeout=0.5)

        logger.info(f"Результат сканирования: найдено {len(modems)} модемов")

        if modems:
            for m in modems:
                logger.info(f"  {m.port}: {m.port_type}")
            port = select_modem_interactive(modems)
        else:
            console.print("\n[yellow]⚠️ Модемы не обнаружены автоматически.[/yellow]")
            console.print(
                "[yellow]💡 Возможно, порт данных (420000 бод) не отвечает на команды.[/yellow]"
            )
            console.print(
                "[yellow]   Вы можете выбрать порт вручную для работы с портом данных.[/yellow]\n"
            )
            port = select_port_manually()

        if port is None:
            return

        # 2. Подключаемся к выбранному порту
        state.port = port
        console.print(f"\n[bold blue]🔄 Подключение к {port}...[/bold blue]")

        handle_connect_modem(port)

        # 3. Главный цикл меню
        while True:
            print_header()

            menu_table = display_menu_table(state)
            console.print(menu_table)

            choice = Prompt.ask("\n[bold cyan]👉 Выберите действие[/bold cyan]")

            handlers = {
                "1": lambda: handle_read_config(port),
                "2": lambda: handle_read_stat(port),
                "3": lambda: handle_set_frequency(port),
                "4": lambda: handle_set_mode(port),
                "5": lambda: handle_set_rate(port),
                "6": lambda: handle_set_protocol(port),
                "7": lambda: handle_set_fhss(port),
                "8": lambda: handle_set_dsss(port),
                "9": lambda: handle_set_pan(port),
                "10": lambda: handle_set_bind(port),
                "11": lambda: handle_toggle_led(port),
                "12": lambda: handle_reboot(port),
                "13": lambda: handle_telemetry_monitor(port),
                "14": lambda: handle_telemetry_collect(port),
                "15": lambda: handle_telemetry_emulate(port),
                "16": lambda: handle_change_port(port),
                "17": lambda: cmd_scan_ports(),
                "18": lambda: cmd_connect_dual(),
                "19": lambda: cmd_sync_modems(),
                "20": lambda: cmd_verify_link(),
                "21": lambda: cmd_disconnect_dual(),
                "0": lambda: handle_exit(port),
            }

            handler = handlers.get(choice)
            if handler:
                result = handler()
                if choice == '16':  # Сменить порт
                    if result:
                        port = result
                        state.port = port
                        console.print("\n[bold blue]🔄 Загрузка конфигурации на новом порту...[/bold blue]")
                        handle_connect_modem(port)
                elif choice == '0':
                    break
                else:
                    # Обработка результата set_parameter
                    if result == 2:
                        # Возврат в главное меню без изменений
                        console.clear()
                        continue
                    elif result != 0:
                        input("\n[yellow]Нажмите Enter для продолжения...[/yellow]")
                    console.clear()
            else:
                console.print("[red]❌ Неверный выбор. Пожалуйста, выберите пункт от 0 до 21.[/red]")
                input("Нажмите Enter для продолжения...")
                console.clear()

    except KeyboardInterrupt:
        console.print("\n\n[bold green]👋 Выход по Ctrl+C. До свидания![/bold green]")
        if state.modem is not None:
            try:
                state.modem.disconnect()
            except:
                pass
        sys.exit(0)