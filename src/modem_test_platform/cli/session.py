"""
Управление состоянием сессии и выполнение команд.
"""

import logging
from datetime import datetime

from rich.console import Console

from modem_test_platform.cli.commands import get_modem
from modem_test_platform.protocols.serial_protocol.exceptions import TransportConnectionError
from modem_test_platform.cli.session_state import get_state

logger = logging.getLogger(__name__)
console = Console()
state = get_state()


def create_args(port: str, **kwargs):
    """Создает объект args для совместимости с существующими командами."""
    class Args:
        pass
    args = Args()
    args.port = port
    for key, value in kwargs.items():
        setattr(args, key, value)
    return args


def execute_command_with_state(func, args, description: str, update_func=None) -> int:
    """Обертка для выполнения команд с обновлением состояния."""
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