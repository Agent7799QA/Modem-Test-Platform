"""
CLI команды для работы с портом данных (CRSF телеметрия).
"""

import signal
import time
from dataclasses import dataclass
from typing import List, Optional

from modem_test_platform.ui.rich_dashboard import TelemetryDashboard, SimpleMonitorDisplay
from modem_test_platform.ui.rich_utils import (
    console,
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
    create_progress_bar,
)

from modem_test_platform.emulation import CommandEmulator
from modem_test_platform.monitoring import RxMonitor, LinkState, StatCollector
from modem_test_platform.transport.serial.serial_transport import SerialTransport


# Убираем импорт get_modem - он не нужен для порта данных


@dataclass
class TelemetryCliConfig:
    """Конфигурация CLI для телеметрии."""
    port: str = "COM8"
    baudrate: int = 420000
    timeout: float = 1.0
    interval: float = 0.25
    duration: Optional[float] = None
    dashboard: bool = True


class TelemetryCli:
    """CLI для работы с телеметрией."""

    def __init__(self, config: TelemetryCliConfig = None):
        self.config = config or TelemetryCliConfig()
        self._running = False
        self._monitor: Optional[RxMonitor] = None
        self._collector: Optional[StatCollector] = None
        self._emulator: Optional[CommandEmulator] = None
        self._dashboard: Optional[TelemetryDashboard] = None
        self._simple_display: Optional[SimpleMonitorDisplay] = None

    def _on_link_state(self, link: LinkState) -> None:
        """Callback при получении LinkState."""
        if self._dashboard and self._dashboard.is_running():
            self._dashboard.update(link, self._collector.get_collection() if self._collector else None)
        elif self._simple_display and self._simple_display._running:
            self._simple_display.update(link, self._collector.get_collection() if self._collector else None)

    def _on_status(self, status: str) -> None:
        """Callback при изменении статуса порта."""
        if self._dashboard and self._dashboard.is_running():
            self._dashboard.update_status(status)
        else:
            if status == "good":
                print_success(f"Порт {self.config.port} подключен")
            elif status == "bad":
                print_error(f"Не удалось подключиться к порту {self.config.port}")
            elif status == "closed":
                print_warning(f"Порт {self.config.port} закрыт")

    def monitor(self, duration: float = None, interval: float = None) -> None:
        """Мониторинг телеметрии в реальном времени."""
        if duration is not None:
            self.config.duration = duration
        if interval is not None:
            self.config.interval = interval

        print_header("МОНИТОРИНГ ТЕЛЕМЕТРИИ")
        print_info(f"Порт: {self.config.port}, скорость: {self.config.baudrate} бод")

        transport = SerialTransport(
            port=self.config.port,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
        )

        try:
            transport.open()
            print_success(f"Подключено к порту {self.config.port}")

            self._monitor = RxMonitor(
                port_name=self.config.port,
                on_status=self._on_status,
            )
            self._monitor._monitor._serial_port = transport._serial

            self._collector = StatCollector()
            self._monitor.on_link_state = self._collector.add_sample

            if self.config.dashboard:
                self._dashboard = TelemetryDashboard(refresh_rate=self.config.interval)
                self._dashboard.start()
                self._monitor.on_link_state = lambda link: self._dashboard.update(
                    link,
                    self._collector.get_collection() if self._collector else None
                )
            else:
                self._simple_display = SimpleMonitorDisplay(refresh_rate=self.config.interval)
                self._simple_display.start()
                self._monitor.on_link_state = lambda link: self._simple_display.update(
                    link,
                    self._collector.get_collection() if self._collector else None
                )

            self._monitor.start()

            if self.config.duration:
                print_info(f"Сбор данных в течение {self.config.duration}с...")
                with create_progress_bar(description="Сбор данных...") as progress:
                    task = progress.add_task("", total=self.config.duration)
                    for _ in range(int(self.config.duration)):
                        if not self._running:
                            break
                        time.sleep(1)
                        progress.update(task, advance=1)
            else:
                print_info("Мониторинг запущен. Нажмите Ctrl+C для остановки.")
                while self._running:
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n")
            print_warning("Остановка по Ctrl+C")
        finally:
            if self._dashboard and self._dashboard.is_running():
                self._dashboard.stop()
            if self._simple_display and self._simple_display._running:
                self._simple_display.stop()
            if self._monitor:
                self._monitor.stop()
            # transport.close()
            # print_info("Отключено от порта")

            if self._collector and not self._collector.is_empty():
                console.print("\n" + "=" * 50)
                console.print("[bold cyan]ФИНАЛЬНАЯ СТАТИСТИКА[/bold cyan]")
                console.print("=" * 50)
                console.print(self._collector.get_summary())
                console.print("=" * 50 + "\n")

    def collect_stats(self, duration: float = 10.0) -> None:
        """Собрать статистику по сигналам."""
        print_header("СБОР СТАТИСТИКИ")
        print_info(f"Порт: {self.config.port}, длительность: {duration}с")

        transport = SerialTransport(
            port=self.config.port,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
        )

        try:
            transport.open()
            print_success(f"Подключено к порту {self.config.port}")

            self._monitor = RxMonitor(
                port_name=self.config.port,
                on_status=self._on_status,
            )
            self._monitor._monitor._serial_port = transport._serial

            self._collector = StatCollector()
            self._monitor.on_link_state = self._collector.add_sample

            self._monitor.start()

            with create_progress_bar(description="Сбор данных...") as progress:
                task = progress.add_task("", total=duration)
                for i in range(int(duration)):
                    if not self._running:
                        break
                    time.sleep(1)
                    progress.update(task, advance=1)

                    if self._collector and not self._collector.is_empty():
                        stats = self._collector.get_collection()
                        progress.console.print(
                            f"  📊 Измерений: {stats.uplink_lq.count}, "
                            f"Uplink LQ: {stats.uplink_lq.min}%/{stats.uplink_lq.max}%/{stats.uplink_lq.avg:.1f}%"
                        )

            print_success("Сбор данных завершен")

            console.print("\n" + "=" * 50)
            console.print("[bold cyan]ФИНАЛЬНАЯ СТАТИСТИКА[/bold cyan]")
            console.print("=" * 50)
            console.print(self._collector.get_summary())
            console.print("=" * 50 + "\n")

        except KeyboardInterrupt:
            print_warning("Остановка по Ctrl+C")
        finally:
            if self._monitor:
                self._monitor.stop()
            # transport.close()
            # print_info("Отключено от порта")

    def emulate(self, channels: List[int], frequency_hz: float = 10.0) -> None:
        """Эмуляция команд."""
        print_header("ЭМУЛЯЦИЯ КОМАНД")
        print_info(f"Порт: {self.config.port}, частота: {frequency_hz} Гц")
        print_info(f"Каналы: {channels[:8]}... (всего {len(channels)})")

        transport = SerialTransport(
            port=self.config.port,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
        )

        try:
            transport.open()
            print_success(f"Подключено к порту {self.config.port}")

            self._emulator = CommandEmulator(transport)
            self._emulator.start_emulation(channels, frequency_hz)

            print_info("Эмуляция запущена. Нажмите Ctrl+C для остановки.")

            with create_progress_bar(description="Отправка команд...") as progress:
                task = progress.add_task("", total=None)
                while self._running:
                    time.sleep(0.5)
                    progress.update(
                        task,
                        description=f"Отправлено: {self._emulator.get_command_count()} команд"
                    )

        except KeyboardInterrupt:
            print_warning("Остановка по Ctrl+C")
        finally:
            if self._emulator:
                self._emulator.stop_emulation()
            transport.close()
            print_info("Отключено от порта")


# ========== Функции для argparse ==========

def parse_channels(channels_str: str) -> List[int]:
    """Парсинг строки с каналами."""
    if not channels_str:
        return []

    parts = channels_str.replace(",", " ").split()
    channels = []
    for part in parts:
        try:
            value = int(part)
            if 0 <= value <= 2047:
                channels.append(value)
            else:
                print(f"⚠️ Значение {value} вне диапазона 0-2047, игнорируем")
        except ValueError:
            print(f"⚠️ Неверное значение '{part}', игнорируем")

    return channels


def add_telemetry_parser(subparsers):
    """Добавить парсеры для команд телеметрии."""

    parser_monitor = subparsers.add_parser(
        "monitor",
        help="Мониторинг телеметрии в реальном времени"
    )
    parser_monitor.add_argument(
        "--port", "-p",
        default="COM8",
        help="COM-порт (по умолчанию: COM8)"
    )
    parser_monitor.add_argument(
        "--duration", "-d",
        type=float,
        help="Длительность мониторинга в секундах"
    )
    parser_monitor.add_argument(
        "--interval", "-i",
        type=float,
        default=0.25,
        help="Интервал обновления в секундах (по умолчанию: 0.25)"
    )
    parser_monitor.set_defaults(func=cli_monitor)

    parser_collect = subparsers.add_parser(
        "collect",
        help="Сбор статистики по сигналам"
    )
    parser_collect.add_argument(
        "--port", "-p",
        default="COM8",
        help="COM-порт (по умолчанию: COM8)"
    )
    parser_collect.add_argument(
        "--duration", "-d",
        type=float,
        default=10.0,
        help="Длительность сбора в секундах (по умолчанию: 10)"
    )
    parser_collect.set_defaults(func=cli_collect)

    parser_emulate = subparsers.add_parser(
        "emulate",
        help="Эмуляция команд (отправка RC-каналов)"
    )
    parser_emulate.add_argument(
        "--port", "-p",
        default="COM8",
        help="COM-порт (по умолчанию: COM8)"
    )
    parser_emulate.add_argument(
        "--channels", "-c",
        type=str,
        default="1500,1500,1500,1500,1000,2000",
        help="Значения каналов через запятую (0-2047), до 16 значений"
    )
    parser_emulate.add_argument(
        "--frequency", "-f",
        type=float,
        default=10.0,
        help="Частота отправки в Гц (по умолчанию: 10)"
    )
    parser_emulate.add_argument(
        "--once", "-o",
        action="store_true",
        help="Отправить один раз и выйти"
    )
    parser_emulate.set_defaults(func=cli_emulate)


# ========== Обработчики команд ==========

def cli_monitor(args):
    config = TelemetryCliConfig(
        port=args.port,
        interval=args.interval,
        duration=args.duration,
    )
    cli = TelemetryCli(config)

    def signal_handler(sig, frame):
        cli._running = False
    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.monitor()


def cli_collect(args):
    config = TelemetryCliConfig(port=args.port)
    cli = TelemetryCli(config)

    def signal_handler(sig, frame):
        cli._running = False
    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.collect_stats(args.duration)


def cli_emulate(args):
    channels = parse_channels(args.channels)
    if not channels:
        print_error("Не заданы каналы")
        return

    config = TelemetryCliConfig(port=args.port)
    cli = TelemetryCli(config)

    def signal_handler(sig, frame):
        cli._running = False
    signal.signal(signal.SIGINT, signal_handler)

    if args.once:
        transport = SerialTransport(port=args.port, baudrate=420000)
        try:
            transport.open()
            emulator = CommandEmulator(transport)
            emulator.send_once(channels)
            print_success(f"Отправлено {len(channels)} каналов: {channels}")
        finally:
            transport.close()
    else:
        cli._running = True
        cli.emulate(channels, args.frequency)