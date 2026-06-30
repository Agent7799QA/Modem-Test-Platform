"""
CLI команды для работы с портом данных (CRSF телеметрия).
"""

import time
import argparse
import signal
from typing import Optional, List
from dataclasses import dataclass

from modem_test_platform.transport.serial.serial_transport import SerialTransport
from modem_test_platform.monitoring import RxMonitor, LinkState, StatCollector, StatCollection
from modem_test_platform.emulation import CommandEmulator, create_default_channels
from modem_test_platform.cli.commands.config_commands import get_modem


@dataclass
class TelemetryCliConfig:
    """Конфигурация CLI для телеметрии."""
    port: str = "COM8"
    baudrate: int = 420000
    timeout: float = 1.0
    interval: float = 0.25  # Интервал обновления в секундах
    duration: Optional[float] = None  # Длительность сбора в секундах


class TelemetryCli:
    """CLI для работы с телеметрией."""

    def __init__(self, config: TelemetryCliConfig = None):
        self.config = config or TelemetryCliConfig()
        self._running = False
        self._monitor: Optional[RxMonitor] = None
        self._collector: Optional[StatCollector] = None
        self._emulator: Optional[CommandEmulator] = None

    def _on_link_state(self, link: LinkState) -> None:
        """Callback при получении LinkState."""
        # Выводим в одной строке с обновлением
        print(f"\r{link}", end="", flush=True)

    def _on_stat_update(self, collection: StatCollection) -> None:
        """Callback при обновлении статистики."""
        stats = collection.to_dict()
        print("\n" + "=" * 50)
        print("📊 СТАТИСТИКА:")
        print(f"  Измерений: {stats['uplink_lq']['count']}")
        print(f"  Длительность: {stats['duration']:.1f}с")
        print(f"  Uplink LQ:   мин={stats['uplink_lq']['min']}%, "
              f"макс={stats['uplink_lq']['max']}%, "
              f"сред={stats['uplink_lq']['avg']:.1f}%")
        print(f"  Uplink RSSI: мин={stats['uplink_rssi']['min']} dBm, "
              f"макс={stats['uplink_rssi']['max']} dBm, "
              f"сред={stats['uplink_rssi']['avg']:.1f} dBm")
        print(f"  Downlink LQ: мин={stats['downlink_lq']['min']}%, "
              f"макс={stats['downlink_lq']['max']}%, "
              f"сред={stats['downlink_lq']['avg']:.1f}%")
        print(f"  Downlink RSSI: мин={stats['downlink_rssi']['min']} dBm, "
              f"макс={stats['downlink_rssi']['max']} dBm, "
              f"сред={stats['downlink_rssi']['avg']:.1f} dBm")
        print("=" * 50)

    def monitor(self, duration: float = None, interval: float = None) -> None:
        """
        Мониторинг телеметрии в реальном времени.

        Args:
            duration: Длительность мониторинга в секундах (None = бесконечно)
            interval: Интервал обновления в секундах
        """
        if duration is not None:
            self.config.duration = duration
        if interval is not None:
            self.config.interval = interval

        # Создаем транспорт
        transport = SerialTransport(
            port=self.config.port,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
        )

        try:
            transport.open()
            print(f"🔌 Подключено к порту {self.config.port} ({self.config.baudrate} бод)")

            # Создаем монитор
            self._monitor = RxMonitor(
                port_name=self.config.port,
                on_link_state=self._on_link_state,
                on_status=self._on_status,
                config=None,  # Используем значения по умолчанию
            )
            # Вручную подключаем транспорт (используем существующий)
            self._monitor._monitor._serial_port = transport._serial

            # Запускаем мониторинг в отдельном потоке
            self._monitor.start()

            # Ожидаем завершения
            if self.config.duration:
                print(f"⏱️ Сбор данных в течение {self.config.duration}с...")
                time.sleep(self.config.duration)
            else:
                print("🔄 Мониторинг запущен. Нажмите Ctrl+C для остановки.")
                while self._running:
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n⏹️ Остановка по Ctrl+C")
        finally:
            if self._monitor:
                self._monitor.stop()
            transport.close()
            print("🔌 Отключено от порта")

    def _on_status(self, status: str) -> None:
        """Callback при изменении статуса порта."""
        status_icons = {
            "good": "✅",
            "bad": "❌",
            "closed": "🔌",
            "write_error": "⚠️",
        }
        icon = status_icons.get(status, "❓")
        if status != "good":
            print(f"\n{icon} Статус порта: {status}")

    def collect_stats(self, duration: float = 10.0) -> None:
        """
        Собрать статистику по сигналам.

        Args:
            duration: Длительность сбора в секундах
        """
        print(f"📊 Сбор статистики в течение {duration}с...")

        # Создаем транспорт
        transport = SerialTransport(
            port=self.config.port,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
        )

        try:
            transport.open()
            print(f"🔌 Подключено к порту {self.config.port}")

            # Создаем монитор
            self._monitor = RxMonitor(
                port_name=self.config.port,
                on_status=self._on_status,
            )
            self._monitor._monitor._serial_port = transport._serial

            # Создаем коллектор
            self._collector = StatCollector(
                on_update=self._on_stat_update,
            )

            # Подключаем коллектор к монитору
            self._monitor.on_link_state = self._collector.add_sample

            # Запускаем
            self._monitor.start()

            # Ждем указанное время
            time.sleep(duration)

            # Выводим финальную статистику
            print("\n📊 ФИНАЛЬНАЯ СТАТИСТИКА:")
            print(self._collector.get_summary())

        except KeyboardInterrupt:
            print("\n⏹️ Остановка по Ctrl+C")
        finally:
            if self._monitor:
                self._monitor.stop()
            transport.close()
            print("🔌 Отключено от порта")

    def emulate(self, channels: List[int], frequency_hz: float = 10.0) -> None:
        """
        Эмуляция команд (отправка RC-каналов).

        Args:
            channels: Список значений каналов (до 16)
            frequency_hz: Частота отправки в Гц
        """
        print(f"🔄 Эмуляция команд на частоте {frequency_hz} Гц")

        # Создаем транспорт
        transport = SerialTransport(
            port=self.config.port,
            baudrate=self.config.baudrate,
            timeout=self.config.timeout,
        )

        try:
            transport.open()
            print(f"🔌 Подключено к порту {self.config.port}")

            # Создаем эмулятор
            self._emulator = CommandEmulator(transport)

            # Запускаем эмуляцию
            self._emulator.start_emulation(channels, frequency_hz)

            print("🔄 Эмуляция запущена. Нажмите Ctrl+C для остановки.")
            while self._running:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n⏹️ Остановка по Ctrl+C")
        finally:
            if self._emulator:
                self._emulator.stop_emulation()
            transport.close()
            print("🔌 Отключено от порта")


# ========== Функции для argparse ==========

def parse_channels(channels_str: str) -> List[int]:
    """
    Парсинг строки с каналами.

    Формат: "1500,1500,1500,..." или "1500 1500 1500..."
    """
    if not channels_str:
        return []

    # Заменяем запятые на пробелы и разбиваем
    parts = channels_str.replace(",", " ").split()
    channels = []
    for part in parts:
        try:
            value = int(part)
            # Проверяем допустимый диапазон (0-2047)
            if 0 <= value <= 2047:
                channels.append(value)
            else:
                print(f"⚠️ Значение {value} вне диапазона 0-2047, игнорируем")
        except ValueError:
            print(f"⚠️ Неверное значение '{part}', игнорируем")

    return channels


def add_telemetry_parser(subparsers):
    """Добавить парсеры для команд телеметрии."""

    # Команда: monitor
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

    # Команда: collect
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

    # Команда: emulate
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
    """Обработчик команды monitor."""
    config = TelemetryCliConfig(
        port=args.port,
        interval=args.interval,
        duration=args.duration,
    )
    cli = TelemetryCli(config)

    # Обработка Ctrl+C
    def signal_handler(sig, frame):
        cli._running = False

    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.monitor()


def cli_collect(args):
    """Обработчик команды collect."""
    config = TelemetryCliConfig(
        port=args.port,
    )
    cli = TelemetryCli(config)

    # Обработка Ctrl+C
    def signal_handler(sig, frame):
        cli._running = False

    signal.signal(signal.SIGINT, signal_handler)

    cli._running = True
    cli.collect_stats(args.duration)


def cli_emulate(args):
    """Обработчик команды emulate."""
    channels = parse_channels(args.channels)
    if not channels:
        print("❌ Не заданы каналы")
        return

    config = TelemetryCliConfig(
        port=args.port,
    )
    cli = TelemetryCli(config)

    # Обработка Ctrl+C
    def signal_handler(sig, frame):
        cli._running = False

    signal.signal(signal.SIGINT, signal_handler)

    if args.once:
        # Отправить один раз
        transport = SerialTransport(port=args.port, baudrate=420000)
        try:
            transport.open()
            emulator = CommandEmulator(transport)
            emulator.send_once(channels)
            print(f"✅ Отправлено {len(channels)} каналов: {channels}")
        finally:
            transport.close()
    else:
        # Непрерывная эмуляция
        cli._running = True
        cli.emulate(channels, args.frequency)