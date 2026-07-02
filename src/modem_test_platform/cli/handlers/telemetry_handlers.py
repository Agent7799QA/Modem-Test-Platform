"""
Обработчики команд телеметрии.
"""

import signal
from datetime import datetime

from rich.prompt import Prompt, Confirm

from modem_test_platform.cli.commands.telemetry_commands import (
    TelemetryCli,
    TelemetryCliConfig,
    parse_channels,
)
from modem_test_platform.cli.session import state
from modem_test_platform.cli.ui.display import console


def handle_telemetry_monitor(port: str) -> int:
    """Запуск мониторинга телеметрии."""
    console.print("[bold blue]📡 Запуск мониторинга телеметрии...[/bold blue]")

    duration_str = Prompt.ask("⏱️ Длительность в секундах", default="0")
    duration = float(duration_str) if duration_str != "0" else None

    interval_str = Prompt.ask("🔄 Интервал обновления (сек)", default="0.25")
    interval = float(interval_str) if interval_str else 0.25

    config = TelemetryCliConfig(port=port, interval=interval, duration=duration)
    cli = TelemetryCli(config)
    state.monitor_active = True

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


def handle_telemetry_collect(port: str) -> int:
    """Сбор статистики телеметрии."""
    console.print("[bold blue]📊 Сбор статистики телеметрии...[/bold blue]")

    duration_str = Prompt.ask("⏱️ Длительность сбора (сек)", default="10")
    duration = float(duration_str) if duration_str else 10.0

    config = TelemetryCliConfig(port=port)
    cli = TelemetryCli(config)

    def signal_handler(sig, frame):
        cli._running = False

    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.collect_stats(duration)

    state.last_command_time = datetime.now().strftime("%H:%M:%S")
    input("\nНажмите Enter для продолжения...")
    console.clear()
    return 0


def handle_telemetry_emulate(port: str) -> int:
    """Эмуляция команд."""
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