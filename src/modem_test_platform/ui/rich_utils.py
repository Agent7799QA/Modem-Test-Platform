"""
Вспомогательные функции для Rich.
"""

from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
from rich import box

from modem_test_platform.monitoring.rx_monitor import LinkState
from modem_test_platform.monitoring.stat_collector import StatCollection

console = Console()


def format_rssi(rssi: int) -> str:
    """Форматировать RSSI с цветом."""
    if rssi >= -60:
        color = "green"
    elif rssi >= -80:
        color = "yellow"
    elif rssi >= -100:
        color = "orange1"
    else:
        color = "red"
    return f"[{color}]{rssi} dBm[/{color}]"


def format_lq(lq: int) -> str:
    """Форматировать LQ с цветом."""
    if lq >= 90:
        color = "green"
    elif lq >= 60:
        color = "yellow"
    else:
        color = "red"
    return f"[{color}]{lq}%[/{color}]"


def format_status(status: str) -> Text:
    """Форматировать статус с цветом."""
    colors = {
        "good": "green",
        "bad": "red",
        "closed": "grey50",
        "write_error": "orange1",
        "connecting": "yellow",
    }
    icons = {
        "good": "✅",
        "bad": "❌",
        "closed": "🔌",
        "write_error": "⚠️",
        "connecting": "🔄",
    }
    color = colors.get(status, "white")
    icon = icons.get(status, "❓")
    return Text(f"{icon} {status}", style=color)


def create_telemetry_table(link: LinkState, stats: Optional[StatCollection] = None) -> Table:
    """
    Создать таблицу с телеметрией.

    Args:
        link: Текущее состояние линка
        stats: Статистика (опционально)

    Returns:
        Table: Таблица для Rich
    """
    table = Table(title="📡 Телеметрия модема", box=box.ROUNDED, show_header=False)
    table.add_column("Параметр", style="cyan", width=20)
    table.add_column("Текущее", style="white", width=20)
    table.add_column("Мин", style="yellow", width=10)
    table.add_column("Макс", style="red", width=10)
    table.add_column("Сред", style="blue", width=10)

    # Uplink LQ
    row = ["Uplink LQ", format_lq(link.uplink_lq)]
    if stats and stats.uplink_lq.count > 0:
        row.extend([
            str(stats.uplink_lq.min) + "%",
            str(stats.uplink_lq.max) + "%",
            f"{stats.uplink_lq.avg:.1f}%"
        ])
    else:
        row.extend(["-", "-", "-"])
    table.add_row(*row)

    # Uplink RSSI
    row = ["Uplink RSSI", format_rssi(link.uplink_rssi)]
    if stats and stats.uplink_rssi.count > 0:
        row.extend([
            str(stats.uplink_rssi.min) + " dBm",
            str(stats.uplink_rssi.max) + " dBm",
            f"{stats.uplink_rssi.avg:.1f} dBm"
        ])
    else:
        row.extend(["-", "-", "-"])
    table.add_row(*row)

    # Downlink LQ
    row = ["Downlink LQ", format_lq(link.downlink_lq)]
    if stats and stats.downlink_lq.count > 0:
        row.extend([
            str(stats.downlink_lq.min) + "%",
            str(stats.downlink_lq.max) + "%",
            f"{stats.downlink_lq.avg:.1f}%"
        ])
    else:
        row.extend(["-", "-", "-"])
    table.add_row(*row)

    # Downlink RSSI
    row = ["Downlink RSSI", format_rssi(link.downlink_rssi)]
    if stats and stats.downlink_rssi.count > 0:
        row.extend([
            str(stats.downlink_rssi.min) + " dBm",
            str(stats.downlink_rssi.max) + " dBm",
            f"{stats.downlink_rssi.avg:.1f} dBm"
        ])
    else:
        row.extend(["-", "-", "-"])
    table.add_row(*row)

    # Дополнительная информация
    if stats and stats.uplink_lq.count > 0:
        table.add_section()
        table.add_row(
            "Измерений",
            str(stats.uplink_lq.count),
            "", "", ""
        )
        table.add_row(
            "Длительность",
            f"{stats.duration:.1f}с",
            "", "", ""
        )

    return table


def create_dashboard(link: LinkState, stats: Optional[StatCollection] = None) -> Panel:
    """
    Создать панель дашборда.

    Args:
        link: Текущее состояние линка
        stats: Статистика (опционально)

    Returns:
        Panel: Панель для Rich
    """
    table = create_telemetry_table(link, stats)
    return Panel(table, title="📡 Modem Telemetry", border_style="cyan")


def create_progress_bar(iterable=None, description: str = "Сбор данных..."):
    """
    Создать прогресс-бар.

    Args:
        iterable: Итерируемый объект (опционально)
        description: Описание прогресса

    Returns:
        Progress: Прогресс-бар
    """
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[progress.description]{description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def print_header(title: str) -> None:
    """Вывести красивый заголовок."""
    console.print(f"\n[bold cyan]{'=' * 50}[/bold cyan]")
    console.print(f"[bold white] {title} [/bold white]")
    console.print(f"[bold cyan]{'=' * 50}[/bold cyan]\n")


def print_success(message: str) -> None:
    """Вывести сообщение об успехе."""
    console.print(f"[green]✅ {message}[/green]")


def print_error(message: str) -> None:
    """Вывести сообщение об ошибке."""
    console.print(f"[red]❌ {message}[/red]")


def print_warning(message: str) -> None:
    """Вывести предупреждение."""
    console.print(f"[yellow]⚠️ {message}[/yellow]")


def print_info(message: str) -> None:
    """Вывести информационное сообщение."""
    console.print(f"[blue]ℹ️ {message}[/blue]")