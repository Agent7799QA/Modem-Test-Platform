"""
Modem Test Platform - CLI (Интерактивное меню с Rich)
"""

import sys
import logging
import serial.tools.list_ports

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

from modem_test_platform.cli.commands import (
    configure_modem,
    set_frequency_cmd,
    set_mode_cmd,
    toggle_led_cmd,
    reboot_cmd,
    read_config_cmd,
    read_stat_cmd,
    get_modem,
)
from modem_test_platform.cli.commands.telemetry_commands import (
    TelemetryCli,
    TelemetryCliConfig,
    parse_channels,
)
from modem_test_platform.transport.exceptions import TransportConnectionError


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rich консоль
console = Console()

# Глобальный объект модема
_modem = None


def list_available_ports() -> list:
    return [p.device for p in serial.tools.list_ports.comports()]


def get_port_from_user() -> str:
    """Запрашивает порт у пользователя с красивым выводом"""
    ports = list_available_ports()

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


def print_header(port: str):
    """Печатает красивый заголовок с Rich"""
    console.clear()

    status = "🟢 Подключен" if _modem and _modem.protocol.transport.is_open else "🔴 Отключен"

    panel = Panel(
        f"[bold cyan]📡 MODEM TEST PLATFORM[/bold cyan]\n"
        f"[white]Интерактивное управление[/white]\n"
        f"[green]🔌 Порт: {port}[/green]  {status}",
        border_style="cyan",
        box=box.DOUBLE,
    )
    console.print(panel)
    console.print()


def execute_command(func, args, description: str = ""):
    """Обертка для выполнения команд с обработкой ошибок"""
    if description:
        console.print(f"[bold blue]⏳ {description}...[/bold blue]")

    try:
        result = func(args)
        if result is not None and result != 0:
            console.print("[red]❌ Команда завершилась с ошибкой[/red]")
            return result
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


def create_args(port: str, **kwargs):
    """Создает объект args для совместимости с существующими командами"""
    class Args:
        pass

    args = Args()
    args.port = port
    for key, value in kwargs.items():
        setattr(args, key, value)
    return args


# ========== Обработчики команд ==========

def handle_configure(port: str):
    """Проверка подключения и чтение конфигурации"""
    global _modem

    # Если модем уже существует, проверяем соединение
    if _modem is not None:
        try:
            # Проверяем, открыт ли порт
            if _modem.protocol.transport.is_open:
                console.print("[green]✅ Модем уже подключен[/green]")
                # Просто читаем конфигурацию
                args = create_args(port)
                return execute_command(read_config_cmd, args, "📖 Чтение конфигурации")
        except:
            pass

    # Создаем новый адаптер
    try:
        _modem = get_modem(port)
        _modem.connect()
        console.print(f"[green]✅ Подключено к модему на порту {port}[/green]")
        args = create_args(port)
        return execute_command(read_config_cmd, args, "📖 Чтение конфигурации")
    except Exception as e:
        console.print(f"[red]❌ Ошибка подключения: {e}[/red]")
        return 1


def handle_read_config(port: str):
    """Чтение конфигурации"""
    global _modem
    if _modem is None:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Проверка подключения'[/red]")
        return 1

    args = create_args(port)
    return execute_command(read_config_cmd, args, "📖 Чтение конфигурации")


def handle_read_stat(port: str):
    """Чтение состояния канала"""
    global _modem
    if _modem is None:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Проверка подключения'[/red]")
        return 1

    args = create_args(port)
    return execute_command(read_stat_cmd, args, "📊 Чтение состояния канала")


def handle_set_frequency(port: str):
    """Установка частоты с выбором"""
    global _modem
    if _modem is None:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Проверка подключения'[/red]")
        return 1

    freq_options = [3500, 4000, 4500, 6500]

    table = Table(title="📡 Доступные частоты", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=6)
    table.add_column("Частота", style="green", width=15)

    for i, freq in enumerate(freq_options, 1):
        table.add_row(str(i), f"{freq} МГц")

    console.print(table)

    while True:
        try:
            choice = Prompt.ask("[bold cyan]Выберите частоту[/bold cyan] (1-4)")
            idx = int(choice) - 1
            if 0 <= idx < len(freq_options):
                freq = freq_options[idx]
                args = create_args(port, frequency=freq)
                return execute_command(set_frequency_cmd, args, f"📡 Установка частоты {freq} МГц")
            else:
                console.print("[red]❌ Неверный выбор[/red]")
        except ValueError:
            console.print("[red]❌ Введите число[/red]")
        except KeyboardInterrupt:
            return 1


def handle_set_mode(port: str):
    """Установка режима с выбором"""
    global _modem
    if _modem is None:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Проверка подключения'[/red]")
        return 1

    mode_options = ["swarm+", "swarm", "longrange"]

    table = Table(title="🔧 Доступные режимы", box=box.ROUNDED)
    table.add_column("№", style="cyan", width=6)
    table.add_column("Режим", style="green", width=15)

    for i, mode in enumerate(mode_options, 1):
        table.add_row(str(i), mode)

    console.print(table)

    while True:
        try:
            choice = Prompt.ask("[bold cyan]Выберите режим[/bold cyan] (1-3)")
            idx = int(choice) - 1
            if 0 <= idx < len(mode_options):
                mode = mode_options[idx]
                args = create_args(port, mode=mode)
                return execute_command(set_mode_cmd, args, f"🔧 Установка режима {mode}")
            else:
                console.print("[red]❌ Неверный выбор[/red]")
        except ValueError:
            console.print("[red]❌ Введите число[/red]")
        except KeyboardInterrupt:
            return 1


def handle_toggle_led(port: str):
    """Переключение LED"""
    global _modem
    if _modem is None:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Проверка подключения'[/red]")
        return 1

    args = create_args(port)
    return execute_command(toggle_led_cmd, args, "💡 Переключение LED")


def handle_reboot(port: str):
    """Перезагрузка модема с подтверждением"""
    global _modem
    if _modem is None:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Проверка подключения'[/red]")
        return 1

    from rich.prompt import Confirm
    if Confirm.ask("[yellow]⚠️  Перезагрузить модем?[/yellow]"):
        args = create_args(port)
        return execute_command(reboot_cmd, args, "🔄 Перезагрузка модема")
    else:
        console.print("[yellow]❌ Отменено[/yellow]")
        return 0


def handle_telemetry_monitor(port: str):
    """Запуск мониторинга телеметрии"""
    # Для телеметрии используем отдельный порт данных
    console.print("[bold blue]📡 Запуск мониторинга телеметрии...[/bold blue]")

    duration_str = Prompt.ask(
        "⏱️ Длительность в секундах",
        default="0",
    )
    duration = float(duration_str) if duration_str != "0" else None

    interval_str = Prompt.ask(
        "🔄 Интервал обновления (сек)",
        default="0.25",
    )
    interval = float(interval_str) if interval_str else 0.25

    config = TelemetryCliConfig(
        port=port,
        interval=interval,
        duration=duration,
    )

    cli = TelemetryCli(config)

    import signal
    def signal_handler(sig, frame):
        cli._running = False
    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.monitor()

    input("\nНажмите Enter для продолжения...")
    console.clear()


def handle_telemetry_collect(port: str):
    """Сбор статистики телеметрии"""
    console.print("[bold blue]📊 Сбор статистики телеметрии...[/bold blue]")

    duration_str = Prompt.ask(
        "⏱️ Длительность сбора (сек)",
        default="10",
    )
    duration = float(duration_str) if duration_str else 10.0

    config = TelemetryCliConfig(port=port)
    cli = TelemetryCli(config)

    import signal
    def signal_handler(sig, frame):
        cli._running = False
    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.collect_stats(duration)

    input("\nНажмите Enter для продолжения...")
    console.clear()


def handle_telemetry_emulate(port: str):
    """Эмуляция команд"""
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
        return

    frequency_str = Prompt.ask(
        "📡 Частота отправки (Гц)",
        default="10",
    )
    frequency = float(frequency_str) if frequency_str else 10.0

    from rich.prompt import Confirm
    once = Confirm.ask("📤 Отправить один раз?")

    config = TelemetryCliConfig(port=port)
    cli = TelemetryCli(config)

    import signal
    def signal_handler(sig, frame):
        cli._running = False
    signal.signal(signal.SIGINT, signal_handler)

    if once:
        from modem_test_platform.transport.serial.serial_transport import SerialTransport
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
        cli._running = True
        cli.emulate(channels, frequency)

    input("\nНажмите Enter для продолжения...")
    console.clear()


def change_port(port: str):
    """Смена порта"""
    global _modem

    # Отключаем текущий модем
    if _modem is not None:
        try:
            _modem.disconnect()
            console.print("[yellow]🔌 Модем отключен от старого порта[/yellow]")
        except:
            pass
        _modem = None

    new_port = get_port_from_user()
    return new_port


def exit_program(port: str):
    """Выход из программы"""
    global _modem

    # Отключаем модем
    if _modem is not None:
        try:
            _modem.disconnect()
            console.print("[green]✅ Модем отключен[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Ошибка при отключении: {e}[/yellow]")

    console.print("\n[bold green]👋 До свидания![/bold green]")
    return 0


# ========== Главное меню ==========

def main():
    """Интерактивное главное меню"""
    global _modem

    try:
        # Сначала выбираем порт
        port = get_port_from_user()

        while True:
            print_header(port)

            # Таблица команд
            menu_table = Table(box=box.ROUNDED)
            menu_table.add_column("№", style="cyan", width=4)
            menu_table.add_column("Команда", style="white")

            menu_items = [
                ("1", "Проверка подключения"),
                ("2", "Чтение конфигурации"),
                ("3", "Чтение состояния канала"),
                ("4", "Установка частоты"),
                ("5", "Установка режима"),
                ("6", "Переключение LED"),
                ("7", "Перезагрузка модема"),
                ("8", "Телеметрия - мониторинг"),
                ("9", "Телеметрия - сбор статистики"),
                ("10", "Телеметрия - эмуляция команд"),
                ("11", "Сменить порт"),
                ("0", "Выход"),
            ]

            for num, desc in menu_items:
                menu_table.add_row(num, desc)

            console.print(menu_table)

            choice = Prompt.ask("\n[bold cyan]👉 Выберите действие[/bold cyan]")

            handlers = {
                '1': lambda: handle_configure(port),
                '2': lambda: handle_read_config(port),
                '3': lambda: handle_read_stat(port),
                '4': lambda: handle_set_frequency(port),
                '5': lambda: handle_set_mode(port),
                '6': lambda: handle_toggle_led(port),
                '7': lambda: handle_reboot(port),
                '8': lambda: handle_telemetry_monitor(port),
                '9': lambda: handle_telemetry_collect(port),
                '10': lambda: handle_telemetry_emulate(port),
                '11': lambda: change_port(port),
                '0': lambda: exit_program(port),
            }

            handler = handlers.get(choice)
            if handler:
                result = handler()
                if choice == '11':
                    # Смена порта
                    if result:
                        port = result
                elif choice == '0':
                    break
                else:
                    if result != 0:
                        input("\n[yellow]Нажмите Enter для продолжения...[/yellow]")
                    console.clear()
            else:
                console.print("[red]❌ Неверный выбор. Пожалуйста, выберите пункт от 0 до 11.[/red]")
                input("Нажмите Enter для продолжения...")
                console.clear()

    except KeyboardInterrupt:
        console.print("\n\n[bold green]👋 Выход по Ctrl+C. До свидания![/bold green]")
        # Попытка отключить модем при Ctrl+C
        if _modem is not None:
            try:
                _modem.disconnect()
            except:
                pass
        sys.exit(0)


if __name__ == "__main__":
    main()