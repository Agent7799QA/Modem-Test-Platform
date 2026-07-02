"""
Modem Test Platform - CLI (Интерактивное меню с Rich)
"""

import sys
import logging
from datetime import datetime
from typing import List, Optional

import serial
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from modem_test_platform.cli.commands import (
    get_modem,
    set_frequency_cmd,
    set_mode_cmd,
    toggle_led_cmd,
    read_stat_cmd,
)
from modem_test_platform.cli.commands.telemetry_commands import (
    TelemetryCli,
    TelemetryCliConfig,
    parse_channels,
)
from modem_test_platform.cli.commands.sync_commands import (
    cmd_scan_ports,
    cmd_connect_dual,
    cmd_sync_modems,
    cmd_verify_link,
    cmd_disconnect_dual,
)
from modem_test_platform.devices.modem.adapter.serial_adapter.port_scanner import (
    ModemInfo,
    scan_ports,
)
from modem_test_platform.protocols.serial_protocol.exceptions import TransportConnectionError
from modem_test_platform.cli.session_state import get_state

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rich консоль
console = Console()

# Глобальное состояние сессии
state = get_state()


def select_port_manually() -> str:
    """Ручной выбор порта (если модемы не найдены)."""
    ports = [p.device for p in serial.tools.list_ports.comports()]

    if not ports:
        console.print("[red]❌ COM-порты не найдены[/red]")
        sys.exit(1)

    console.print("[yellow]⚠️ Модемы не обнаружены автоматически.[/yellow]")
    console.print("[yellow]💡 Возможно, порт данных (420000 бод) не отвечает на команды.[/yellow]")
    console.print(
        "[yellow]   Вы можете выбрать порт вручную для работы с портом данных.[/yellow]\n"
    )

    table = Table(title="📡 Доступные COM-порты", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=6)
    table.add_column("Порт", style="green", width=15)

    for i, port in enumerate(ports, 1):
        table.add_row(str(i), port)

    console.print(table)

    while True:
        try:
            choice = Prompt.ask(
                "\n[bold cyan]Выберите номер порта[/bold cyan] (или 'q' для выхода)"
            )
            if choice.lower() == "q":
                console.print("[yellow]👋 Выход по запросу пользователя[/yellow]")
                sys.exit(0)

            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                port = ports[idx]
                console.print(f"[green]✅ Выбран порт: {port}[/green]")
                return port
        except ValueError:
            console.print("[red]❌ Введите число[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Выход по Ctrl+C[/yellow]")
            sys.exit(0)
            
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


def get_port_from_user() -> str:
    """Запрашивает порт у пользователя с красивым выводом"""
    ports = [p.device for p in serial.tools.list_ports.comports()]

    if not ports:
        console.print("[red]❌ COM-порты не найдены[/red]")
        sys.exit(1)

    table = Table(title="📡 Доступные COM-порты", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=6)
    table.add_column("Порт", style="green", width=15)

    for i, port in enumerate(ports, 1):
        table.add_row(str(i), port)

    console.print(table)

    while True:
        try:
            choice = Prompt.ask(
                "\n[bold cyan]Выберите номер порта[/bold cyan] (или 'q' для выхода)"
            )

            if choice.lower() == 'q':
                console.print("[yellow]👋 Выход по запросу пользователя[/yellow]")
                sys.exit(0)

            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                port = ports[idx]
                console.print(f"[green]✅ Выбран порт: {port}[/green]")
                return port
            else:
                console.print(f"[red]❌ Неверный номер. Введите число от 1 до {len(ports)}[/red]")
        except ValueError:
            console.print("[red]❌ Пожалуйста, введите число или 'q' для выхода[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Выход по Ctrl+C[/yellow]")
            sys.exit(0)


def print_header():
    """Печатает красивый заголовок без статуса"""
    console.clear()

    panel = Panel(
        "[bold cyan]📡 MODEM TEST PLATFORM[/bold cyan]\n[white]Интерактивное управление[/white]",
        border_style="cyan",
        box=box.DOUBLE,
        width=80,
    )
    console.print(panel, justify="center")


def create_args(port: str, **kwargs):
    """Создает объект args для совместимости с существующими командами"""
    class Args:
        pass

    args = Args()
    args.port = port
    for key, value in kwargs.items():
        setattr(args, key, value)
    return args


def execute_command_with_state(func, args, description: str, update_func=None):
    """Обертка для выполнения команд с обновлением состояния"""
    if description:
        console.print(f"[bold blue]⏳ {description}...[/bold blue]")

    try:
        result = func(args)
        if result is not None and result != 0:
            console.print("[red]❌ Команда завершилась с ошибкой[/red]")
            return result

        if update_func:
            update_func()

        console.print("[green]✅ Команда выполнена успешно![/green]")
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹ Прервано пользователем[/yellow]")
        return 1
    except TransportConnectionError as e:
        console.print(f"[red]❌ Ошибка подключения: {e}[/red]")
        return 1
    except Exception as e:
        console.print(f"[red]❌ Неожиданная ошибка: {e}[/red]")
        logger.exception("Неожиданная ошибка")
        return 1


# ============================================================
#  ОБЩАЯ ФУНКЦИЯ set_parameter
# ============================================================

def set_parameter(
    options: list,
    display_map: dict,
    get_current: callable,
    setter: callable,
    description: str,
    mode: str = "set"  # "set" или "toggle"
) -> int:
    """
    Общая функция для выбора и установки параметра.

    Args:
        options: Список допустимых значений
        display_map: Словарь {значение: строка для отображения}
        get_current: Функция, возвращающая текущее значение из state
        setter: Функция, принимающая значение и возвращающая bool
        description: Описание параметра для заголовка
        mode: "set" — выбор из списка, "toggle" — просто переключение

    Returns:
        0 при успехе, иначе 1
    """
    if mode == "toggle":
        # Для toggle-параметров (LED, EW tests и т.д.)
        console.print(f"[bold blue]🔄 {description}...[/bold blue]")
        result = setter()  # setter не принимает аргументов
        if result:
            console.print(f"[green]✅ {description} переключен[/green]")
            return 0
        else:
            console.print(f"[red]❌ Не удалось переключить {description}[/red]")
            return 1

    # Режим "set" — выбор из списка
    table = Table(title=f"📡 {description}", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=6)
    table.add_column("Значение", style="green", width=20)

    current = get_current()
    for i, opt in enumerate(options, 1):
        marker = " ✅" if opt == current else ""
        display = display_map.get(opt, str(opt))
        table.add_row(str(i), f"{display}{marker}")

    console.print(table)

    while True:
        try:
            choice = Prompt.ask(f"[bold cyan]Выберите {description.lower()}[/bold cyan] (1-{len(options)})")
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                value = options[idx]
                result = setter(value)
                if result:
                    console.print(f"[green]✅ {description} установлен на {display_map.get(value, value)}[/green]")
                    return 0
                else:
                    console.print(f"[red]❌ Не удалось установить {description}[/red]")
                    return 1
            else:
                console.print("[red]❌ Неверный выбор[/red]")
        except ValueError:
            console.print("[red]❌ Введите число[/red]")
        except KeyboardInterrupt:
            return 1


# ============================================================
#  ОБРАБОТЧИКИ КОМАНД (с использованием set_parameter)
# ============================================================

def handle_read_config(port: str) -> int:
    """Перечитать конфигурацию (только print, без stat)"""
    global state

    console.print("[bold blue]📖 Перечитывание конфигурации...[/bold blue]")

    try:
        if state.modem is None:
            state.modem = get_modem(port)
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

    except TransportConnectionError as e:
        console.print(f"[red]❌ Ошибка подключения: {e}[/red]")
        return 1
    except Exception as e:
        console.print(f"[red]❌ Ошибка: {e}[/red]")
        logger.exception("Ошибка при чтении конфигурации")
        return 1


def handle_read_stat(port: str):
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


def handle_set_frequency(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = [3500, 4000, 4500, 6500]
    display_map = {f: f"{f} МГц" for f in options}
    get_current = lambda: state.frequency
    setter = lambda v: state.modem.set_frequency(v)

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=get_current,
        setter=setter,
        description="Частота"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_mode(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = ["swarm+", "swarm", "longrange"]
    display_map = {m: m for m in options}
    get_current = lambda: state.mode
    setter = lambda v: state.modem.set_mode(v)

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=get_current,
        setter=setter,
        description="Режим"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_rate(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = [5, 10, 25, 40, 50]
    display_map = {r: f"{r} Гц" for r in options}
    get_current = lambda: state.link_rate
    setter = lambda v: state.modem.set_rate(v)

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=get_current,
        setter=setter,
        description="Скорость"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_protocol(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = ["crsf", "sbus", "mavlink", "raw"]
    display_map = {p: p for p in options}
    get_current = lambda: state.protocol
    setter = lambda v: state.modem.set_protocol(v)

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=get_current,
        setter=setter,
        description="Протокол"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_fhss(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = [0, 1, 2, 3, 4]
    fhss_desc = {
        0: "Выключен",
        1: "3.5, 4.0 ГГц",
        2: "4.0, 4.5 ГГц",
        3: "3.5, 4.5 ГГц",
        4: "3.5, 4.0, 4.5 ГГц",
    }
    display_map = {m: f"{m} - {fhss_desc[m]}" for m in options}
    get_current = lambda: state.fhss
    setter = lambda v: state.modem.set_fhss_mode(v)

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=get_current,
        setter=setter,
        description="FHSS"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_dsss(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = [0, 1, 2, 3, 7]
    dsss_desc = {
        0: "Выключен",
        1: "16 MHz коды",
        2: "64 MHz коды",
        3: "16 и 64 MHz коды",
        7: "Все коды",
    }
    display_map = {m: f"{m} - {dsss_desc[m]}" for m in options}
    get_current = lambda: state.dsss
    setter = lambda v: state.modem.set_dsss_mode(v)

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=get_current,
        setter=setter,
        description="DSSS"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_pan(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    try:
        current = state.network_address if state.network_address is not None else 0
        pan = Prompt.ask(
            f"[bold cyan]Введите адрес сети (PAN)[/bold cyan] (0-65534)",
            default=str(current)
        )
        pan = int(pan)

        if 0 <= pan <= 65534:
            result = state.modem.set_pan(pan)
            if result:
                state.network_address = pan
                state.last_command_time = datetime.now().strftime("%H:%M:%S")
                console.print(f"[green]✅ Адрес сети установлен на {pan}[/green]")
                return 0
            else:
                console.print("[red]❌ Не удалось установить адрес сети[/red]")
                return 1
        else:
            console.print("[red]❌ Неверное значение. Должно быть 0-65534[/red]")
            return 1
    except ValueError:
        console.print("[red]❌ Введите число[/red]")
        return 1


def handle_set_bind(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    try:
        current = state.bind_address if state.bind_address is not None else 0
        bind = Prompt.ask(
            f"[bold cyan]Введите адрес управления (BIND)[/bold cyan] (0-65534)",
            default=str(current)
        )
        bind = int(bind)

        if 0 <= bind <= 65534:
            result = state.modem.set_bind_address(bind)
            if result:
                state.bind_address = bind
                state.last_command_time = datetime.now().strftime("%H:%M:%S")
                console.print(f"[green]✅ Адрес управления установлен на {bind}[/green]")
                return 0
            else:
                console.print("[red]❌ Не удалось установить адрес управления[/red]")
                return 1
        else:
            console.print("[red]❌ Неверное значение. Должно быть 0-65534[/red]")
            return 1
    except ValueError:
        console.print("[red]❌ Введите число[/red]")
        return 1


def handle_toggle_led(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    result = set_parameter(
        options=[],  # не используется
        display_map={},
        get_current=lambda: state.led_state,
        setter=lambda: state.modem.toggle_led(),
        description="LED",
        mode="toggle"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_reboot(port: str):
    global state
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    if Confirm.ask("[yellow]⚠️  Перезагрузить модем?[/yellow]"):
        try:
            result = state.modem.reboot()
            if result:
                console.print("[green]✅ Модем перезагружен успешно[/green]")
                state.last_reboot_time = datetime.now().strftime("%H:%M:%S")
                config = state.modem.read_configuration()
                if config:
                    state.update_from_config(config)
                    console.print("[green]✅ Конфигурация после перезагрузки получена[/green]")
                state.last_command_time = datetime.now().strftime("%H:%M:%S")
                return 0
            else:
                console.print("[red]❌ Модем не перезагрузился[/red]")
                return 1
        except Exception as e:
            console.print(f"[red]❌ Ошибка при перезагрузке: {e}[/red]")
            return 1
    else:
        console.print("[yellow]❌ Отменено[/yellow]")
        return 0


def handle_telemetry_monitor(port: str):
    global state
    console.print("[bold blue]📡 Запуск мониторинга телеметрии...[/bold blue]")

    duration_str = Prompt.ask("⏱️ Длительность в секундах", default="0")
    duration = float(duration_str) if duration_str != "0" else None

    interval_str = Prompt.ask("🔄 Интервал обновления (сек)", default="0.25")
    interval = float(interval_str) if interval_str else 0.25

    config = TelemetryCliConfig(port=port, interval=interval, duration=duration)
    cli = TelemetryCli(config)
    state.monitor_active = True

    import signal
    def signal_handler(sig, frame):
        cli._running = False
        state.monitor_active = False
    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.monitor()
    state.monitor_active = False
    state.last_command_time = datetime.now().strftime("%H:%M:%S")

    input("\nНажмите Enter для продолжения...")
    console.clear()
    return 0


def handle_telemetry_collect(port: str):
    global state
    console.print("[bold blue]📊 Сбор статистики телеметрии...[/bold blue]")

    duration_str = Prompt.ask("⏱️ Длительность сбора (сек)", default="10")
    duration = float(duration_str) if duration_str else 10.0

    config = TelemetryCliConfig(port=port)
    cli = TelemetryCli(config)

    import signal
    def signal_handler(sig, frame):
        cli._running = False
    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.collect_stats(duration)

    state.last_command_time = datetime.now().strftime("%H:%M:%S")
    input("\nНажмите Enter для продолжения...")
    console.clear()
    return 0


def handle_telemetry_emulate(port: str):
    global state
    console.print("[bold blue]🎮 Эмуляция команд...[/bold blue]")

    channels_str = Prompt.ask(
        "📊 Введите каналы через запятую",
        default="1500,1500,1500,1500,1000,2000"
    )
    channels = parse_channels(channels_str)
    if not channels:
        console.print("[red]❌ Неверные каналы[/red]")
        input("\nНажмите Enter для продолжения...")
        console.clear()
        return 1

    frequency_str = Prompt.ask("📡 Частота отправки (Гц)", default="10")
    frequency = float(frequency_str) if frequency_str else 10.0
    once = Confirm.ask("📤 Отправить один раз?")

    config = TelemetryCliConfig(port=port)
    cli = TelemetryCli(config)

    import signal
    def signal_handler(sig, frame):
        cli._running = False
        state.emulation_active = False
    signal.signal(signal.SIGINT, signal_handler)

    if once:
        from modem_test_platform.protocols.serial_protocol.serial_transport import SerialTransport
        from modem_test_platform.emulation import CommandEmulator

        transport = SerialTransport(port=port, baudrate=420000)
        try:
            transport.open()
            emulator = CommandEmulator(transport)
            emulator.send_once(channels)
            console.print(f"[green]✅ Отправлено {len(channels)} каналов: {channels}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Ошибка: {e}[/red]")
        finally:
            transport.close()
    else:
        state.emulation_active = True
        state.emulation_freq = frequency
        cli._running = True
        cli.emulate(channels, frequency)
        state.emulation_active = False

    state.last_command_time = datetime.now().strftime("%H:%M:%S")
    input("\nНажмите Enter для продолжения...")
    console.clear()
    return 0


def change_port(port: str):
    global state
    if state.modem is not None:
        try:
            state.modem.disconnect()
        except:
            pass
        state.modem = None
        state.is_connected = False

    new_port = get_port_from_user()
    return new_port


def exit_program(port: str):
    global state
    if state.modem is not None:
        try:
            state.modem.disconnect()
            console.print("[green]✅ Модем отключен[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Ошибка при отключении: {e}[/yellow]")
    console.print("\n[bold green]👋 До свидания![/bold green]")
    return 0


def select_modem_interactive(modems: List[ModemInfo]) -> Optional[str]:
    """Интерактивный выбор модема из списка."""
    if not modems:
        return None

    # Сначала показываем найденные модемы
    display_modems(modems)

    # Предлагаем выбор
    choices = [str(i) for i in range(1, len(modems) + 1)]
    while True:
        try:
            choice = Prompt.ask(
                "\n[bold cyan]Выберите номер модема для подключения[/bold cyan] (или 'q' для выхода)",
                choices=choices + ["q"]
            )
            if choice.lower() == 'q':
                console.print("[yellow]👋 Выход по запросу пользователя[/yellow]")
                sys.exit(0)

            idx = int(choice) - 1
            if 0 <= idx < len(modems):
                port = modems[idx].port
                console.print(f"[green]✅ Выбран порт: {port} ({modems[idx].port_type})[/green]")
                return port
        except ValueError:
            console.print("[red]❌ Пожалуйста, введите число[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Выход по Ctrl+C[/yellow]")
            sys.exit(0)


# ============================================================
#  ГЛАВНОЕ МЕНЮ
# ============================================================

def main():
    global state

    try:
        # 1. Сканируем порты
        console.print("\n[bold blue]🔍 Сканирование портов...[/bold blue]")
        modems = scan_ports()

        if modems:
            # Модемы найдены — выбор из списка
            port = select_modem_interactive(modems)
        else:
            # Модемы не найдены — ручной выбор
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

        try:
            state.modem = get_modem(port)
            state.modem.connect()
            console.print(f"[green]✅ Подключено к модему на порту {port}[/green]")

            config = state.modem.read_configuration()
            if config:
                state.update_from_config(config)
                console.print("[green]✅ Конфигурация загружена[/green]")
                state.last_command_time = datetime.now().strftime("%H:%M:%S")
            else:
                console.print("[yellow]⚠️ Не удалось загрузить конфигурацию[/yellow]")
                console.print(
                    "[yellow]   Возможно, это порт данных (скорость 420000 бод).[/yellow]"
                )
                console.print(
                    "[yellow]   Для управления модемом используйте порт конфигурации (115200 бод).[/yellow]"
                )
        except Exception as e:
            console.print(f"[red]❌ Ошибка при подключении: {e}[/red]")
            console.print("[yellow]⚠️ Некоторые команды могут быть недоступны.[/yellow]")
            console.print(
                "[yellow]   Проверьте, что вы подключились к порту конфигурации (115200 бод).[/yellow]"
            )
        # 4. Запускаем главное меню
        while True:
            print_header()

            menu_table = Table(box=box.ROUNDED)
            menu_table.add_column("№", style="cyan", width=4)
            menu_table.add_column("Команда", style="white")
            menu_table.add_column("Текущее состояние", style="green", width=40)

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
                menu_table.add_row(num, desc, status)

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
                "16": lambda: change_port(port),
                "17": lambda: cmd_scan_ports(),
                "18": lambda: cmd_connect_dual(),
                "19": lambda: cmd_sync_modems(),
                "20": lambda: cmd_verify_link(),
                "21": lambda: cmd_disconnect_dual(),
                "0": lambda: exit_program(port),
            }

            handler = handlers.get(choice)
            if handler:
                result = handler()
                if choice == '16':  # Сменить порт
                    if result:
                        port = result
                        state.port = port
                        console.print("\n[bold blue]🔄 Загрузка конфигурации на новом порту...[/bold blue]")
                        try:
                            if state.modem is None:
                                state.modem = get_modem(port)
                            state.modem.connect()
                            config = state.modem.read_configuration()
                            if config:
                                state.update_from_config(config)
                                console.print("[green]✅ Конфигурация загружена[/green]")
                                state.last_command_time = datetime.now().strftime("%H:%M:%S")
                        except Exception as e:
                            console.print(f"[red]❌ Ошибка: {e}[/red]")
                elif choice == '0':
                    break
                else:
                    if result != 0:
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


if __name__ == "__main__":
    main()