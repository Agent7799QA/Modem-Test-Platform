"""
Функции для ввода данных пользователем.
"""

import sys
import serial
from typing import List, Optional

from rich.prompt import Prompt
from rich.table import Table
from rich import box

from modem_test_platform.cli.ui.display import console, display_modems
from modem_test_platform.devices.modem.adapter.serial_adapter.port_scanner import ModemInfo


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


def select_modem_interactive(modems: List[ModemInfo]) -> Optional[str]:
    """Интерактивный выбор модема из списка."""
    if not modems:
        return None

    display_modems(modems)

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