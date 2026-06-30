"""
Тестирование работы с модемом через новую архитектуру
"""

import argparse
import logging
import textwrap
import serial.tools.list_ports

from modem_test_platform.transport.exceptions import TransportConnectionError
from modem_test_platform.transport.serial.serial_transport import SerialTransport
from modem_test_platform.protocols.crossfire.crossfire_protocol import CrossfireProtocol
from modem_test_platform.devices.adapters.crossfire.crossfire_adapter import CrossfireAdapter

# Импортируем команды телеметрии
from modem_test_platform.cli.commands.telemetry_commands import add_telemetry_parser


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_message(logger, level: str, message: str, width: int = 80) -> None:
    """Вывод сообщения с переносом длинных строк."""
    wrapped = textwrap.fill(str(message), width=width, subsequent_indent=" " * 4)
    getattr(logger, level)(wrapped)


def list_available_ports() -> list:
    return [p.device for p in serial.tools.list_ports.comports()]


def get_port_from_user() -> str:
    ports = list_available_ports()

    if not ports:
        logger.error("COM-порты не найдены")
        exit(1)

    logger.info("Доступные порты: %s", ports)
    print("\nДоступные COM-порты:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")

    while True:
        try:
            choice = input("\nВыберите номер порта (или 'q' для выхода): ").strip()
            if choice.lower() == 'q':
                logger.info("Выход по запросу пользователя")
                exit(0)

            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                logger.info("Выбран порт: %s", ports[idx])
                return ports[idx]
            else:
                print(f"❌ Неверный номер. Введите число от 1 до {len(ports)}")
        except ValueError:
            print("❌ Пожалуйста, введите число или 'q' для выхода")
        except KeyboardInterrupt:
            logger.info("Выход по Ctrl+C")
            exit(0)


# ========== Команды для порта конфигурации ==========

def cmd_configure(args):
    """Команда: проверить подключение к модему."""
    logger.info("Запуск теста подключения к модему")

    port = args.port

    try:
        # Создание транспорта для порта управления (скорость 115200)
        transport = SerialTransport(port=port, baudrate=115200, timeout=2.0)
        logger.debug("Транспорт создан для порта %s", port)

        protocol = CrossfireProtocol(transport)
        logger.debug("Протокол CRSF создан")

        modem = CrossfireAdapter(protocol)
        logger.debug("Адаптер модема создан")

        # Чтение конфигурации (автоматически открывает порт)
        logger.info("Чтение конфигурации...")
        config = modem.read_configuration()
        if config:
            log_message(logger, "info", f"Конфигурация получена:\n{config}")
        else:
            logger.warning("Конфигурация не получена")

        # Чтение состояния канала
        logger.info("Чтение состояния канала...")
        state = modem.read_link_state()
        if state:
            log_message(logger, "info", f"Состояние получено:\n{state}")
        else:
            logger.warning("Состояние не получено")

        # Отключение
        logger.info("Отключение от модема...")
        modem.disconnect()
        logger.info("Отключено")

    except TransportConnectionError as e:
        logger.error(e)
        return 1
    except Exception:
        logger.exception("Неожиданная ошибка")
        return 1

    return 0


# ========== Главная функция ==========

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Modem Test Platform - управление модемом и телеметрия"
    )
    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # Команда: configure - работа с портом конфигурации
    parser_configure = subparsers.add_parser(
        "configure",
        help="Работа с портом конфигурации (115200 бод)"
    )
    parser_configure.add_argument(
        "--port", "-p",
        help="COM-порт (если не указан, будет запрошен)"
    )
    parser_configure.set_defaults(func=cmd_configure)

    # Добавляем команды телеметрии
    add_telemetry_parser(subparsers)

    # Разбираем аргументы
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # Если порт не указан для configure, запрашиваем
    if args.command == "configure" and not args.port:
        args.port = get_port_from_user()

    # Выполняем команду
    try:
        result = args.func(args)
        if result is not None:
            exit(result)
    except KeyboardInterrupt:
        logger.info("Выход по Ctrl+C")
        exit(0)


if __name__ == "__main__":
    main()