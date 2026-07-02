"""
Вспомогательные UI-функции.
"""

from rich.table import Table
from rich.prompt import Prompt
from rich import box

from modem_test_platform.cli.ui.display import console


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
        0 при успехе, 1 при ошибке, 2 при возврате в главное меню
    """
    if mode == "toggle":
        # Для toggle-параметров (LED, EW tests и т.д.)
        console.print(f"[bold blue]🔄 {description}...[/bold blue]")
        result = setter()
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
    current_str = str(current).lower().strip() if current is not None else ""

    for i, opt in enumerate(options, 1):
        opt_str = str(opt).lower().strip()
        marker = " ✅" if opt_str == current_str else ""
        display = display_map.get(opt, str(opt))
        table.add_row(str(i), f"{display}{marker}")

    console.print(table)

    while True:
        try:
            choice = Prompt.ask(
                f"[bold cyan]Выберите {description.lower()}[/bold cyan] (0 - назад, 1-{len(options)})"
            )

            if choice == "0":
                console.print("[yellow]↩️ Возврат в главное меню[/yellow]")
                return 2

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