"""
Тестирование работы с модемом через новую архитектуру
"""

import logging
import textwrap
import serial.tools.list_ports

from modem_test_platform.transport.serial.serial_transport import SerialTransport
from modem_test_platform.protocols.crossfire.crossfire_protocol import CrossfireProtocol
from modem_test_platform.devices.adapters.crossfire.crossfire_adapter import CrossfireAdapter


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


def main() -> None:
    logger.info("Запуск теста подключения к модему")

    port = get_port_from_user()

    try:
        transport = SerialTransport(port, 420000)
        logger.debug("Транспорт создан для порта %s", port)

        protocol = CrossfireProtocol(transport)
        logger.debug("Протокол CRSF создан")

        modem = CrossfireAdapter(protocol)
        logger.debug("Адаптер модема создан")

        logger.info("Подключение к модему...")
        modem.connect()
        logger.info("Подключено к %s", port)

        logger.info("Чтение конфигурации...")
        config = modem.read_configuration()
        if config:
            log_message(logger, "info", f"Конфигурация получена:\n{config}")
        else:
            logger.warning("Конфигурация не получена")

        logger.info("Чтение состояния канала...")
        state = modem.read_link_state()
        if state:
            log_message(logger, "info", f"Состояние получено:\n{state}")
        else:
            logger.warning("Состояние не получено")

        logger.info("Отключение от модема...")
        modem.disconnect()
        logger.info("Отключено")

    except Exception as e:
        logger.exception("Ошибка при работе с модемом: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    main()