"""
Обработчики команд настройки параметров модема.
"""

from datetime import datetime

from rich.prompt import Prompt, Confirm

from modem_test_platform.cli.session import state
from modem_test_platform.cli.ui.utils import set_parameter
from modem_test_platform.cli.ui.display import console


def handle_set_frequency(port: str) -> int:
    """Установка частоты."""
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = [3500, 4000, 4500, 6500]
    display_map = {f: f"{f} МГц" for f in options}

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=lambda: state.frequency,
        setter=lambda v: state.modem.set_frequency(v),
        description="Частота"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_mode(port: str) -> int:
    """Установка режима."""
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = ["swarm+", "swarm", "longrange"]
    display_map = {m: m for m in options}

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=lambda: state.mode,
        setter=lambda v: state.modem.set_mode(v),
        description="Режим"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_rate(port: str) -> int:
    """Установка скорости (rate)."""
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = [5, 10, 25, 40, 50]
    display_map = {r: f"{r} Гц" for r in options}

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=lambda: state.link_rate,
        setter=lambda v: state.modem.set_rate(v),
        description="Скорость"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_protocol(port: str) -> int:
    """Установка протокола."""
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    options = ["crsf", "sbus", "mavlink", "raw"]
    display_map = {p: p for p in options}

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=lambda: state.protocol,
        setter=lambda v: state.modem.set_protocol(v),
        description="Протокол"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_fhss(port: str) -> int:
    """Установка FHSS."""
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

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=lambda: state.fhss,
        setter=lambda v: state.modem.set_fhss_mode(v),
        description="FHSS"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_dsss(port: str) -> int:
    """Установка DSSS."""
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

    result = set_parameter(
        options=options,
        display_map=display_map,
        get_current=lambda: state.dsss,
        setter=lambda v: state.modem.set_dsss_mode(v),
        description="DSSS"
    )

    if result == 0:
        config = state.modem.read_configuration()
        if config:
            state.update_from_config(config)
        state.last_command_time = datetime.now().strftime("%H:%M:%S")
    return result


def handle_set_pan(port: str) -> int:
    """Установка адреса сети (PAN)."""
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


def handle_set_bind(port: str) -> int:
    """Установка адреса управления (BIND)."""
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


def handle_toggle_led(port: str) -> int:
    """Переключение LED."""
    if state.modem is None or not state.modem.protocol.transport.is_open:
        console.print("[red]❌ Модем не подключен. Сначала выполните 'Перечитать конфигурацию'[/red]")
        return 1

    result = set_parameter(
        options=[],
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


def handle_reboot(port: str) -> int:
    """Перезагрузка модема."""
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