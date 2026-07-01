"""
CLI команды для работы с портом конфигурации модема.
"""

import logging

from modem_test_platform.devices.adapters.crossfire.crossfire_adapter import CrossfireAdapter
from modem_test_platform.protocols.crossfire.crossfire_protocol import CrossfireProtocol
from modem_test_platform.transport.serial.serial_transport import SerialTransport

logger = logging.getLogger(__name__)


def get_modem(port: str, baudrate: int = 115200, timeout: float = 2.0) -> CrossfireAdapter:
    """
    Создать и вернуть адаптер модема для порта конфигурации.

    Args:
        port: COM-порт
        baudrate: Скорость (по умолчанию 115200)
        timeout: Таймаут в секундах

    Returns:
        CrossfireAdapter: Адаптер модема
    """
    transport = SerialTransport(port=port, baudrate=baudrate, timeout=timeout)
    protocol = CrossfireProtocol(transport)
    modem = CrossfireAdapter(protocol)
    return modem


def configure_modem(args) -> int:
    """Команда: проверить подключение к модему и прочитать конфигурацию."""
    port = args.port  # ✅ Добавлено: получаем порт из args

    try:
        modem = get_modem(port)
        modem.connect()

        logger.info("Чтение конфигурации...")
        config = modem.read_configuration()
        if config:
            logger.info("Конфигурация получена:\n%s", config)
        else:
            logger.warning("Конфигурация не получена")
            return 1

        logger.info("Чтение состояния канала...")
        state = modem.read_link_state()
        if state:
            logger.info("Состояние получено:\n%s", state)
        else:
            logger.warning("Состояние не получено")

        # modem.disconnect()  # ❌ НЕ ОТКЛЮЧАЕМСЯ - оставляем соединение открытым
        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def set_frequency_cmd(args) -> int:
    """Команда: установка частоты."""
    try:
        modem = get_modem(args.port)
        modem.connect()

        logger.info("Установка частоты %d МГц...", args.frequency)
        result = modem.set_frequency(args.frequency)

        if result:
            logger.info("✅ Частота успешно установлена")
        else:
            logger.warning("⚠️ Не удалось установить частоту")
            return 1

        # modem.disconnect()  # ❌ НЕ ОТКЛЮЧАЕМСЯ
        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def set_mode_cmd(args) -> int:
    """Команда: установка режима."""
    try:
        modem = get_modem(args.port)
        modem.connect()

        logger.info("Установка режима %s...", args.mode)
        result = modem.set_mode(args.mode)

        if result:
            logger.info("✅ Режим успешно установлен")
        else:
            logger.warning("⚠️ Не удалось установить режим")
            return 1

        # modem.disconnect()  # ❌ НЕ ОТКЛЮЧАЕМСЯ
        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def toggle_led_cmd(args) -> int:
    """Команда: переключение LED."""
    try:
        modem = get_modem(args.port)
        modem.connect()

        logger.info("Переключение LED...")
        result = modem.toggle_led()

        if result:
            logger.info("✅ LED переключен")
        else:
            logger.warning("⚠️ Не удалось переключить LED")
            return 1

        # modem.disconnect()  # ❌ НЕ ОТКЛЮЧАЕМСЯ
        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def reboot_cmd(args) -> int:
    """Команда: перезагрузка модема."""
    try:
        modem = get_modem(args.port)
        modem.connect()

        logger.info("Перезагрузка модема...")
        result = modem.reboot()

        if result:
            logger.info("✅ Модем перезагружен")
        else:
            logger.warning("⚠️ Не удалось перезагрузить модем")
            return 1

        # modem.disconnect()  # ❌ НЕ ОТКЛЮЧАЕМСЯ (после reboot соединение может восстановиться)
        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def read_config_cmd(args) -> int:
    """Команда: чтение конфигурации."""
    try:
        modem = get_modem(args.port)
        modem.connect()

        logger.info("Чтение конфигурации...")
        config = modem.read_configuration()

        if config:
            logger.info("Конфигурация:\n%s", config)
        else:
            logger.warning("Конфигурация не получена")
            return 1

        # modem.disconnect()  # ❌ НЕ ОТКЛЮЧАЕМСЯ
        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def read_stat_cmd(args) -> int:
    """Команда: чтение состояния канала."""
    try:
        modem = get_modem(args.port)
        modem.connect()

        logger.info("Чтение состояния канала...")
        state = modem.read_link_state()

        if state:
            logger.info("Состояние:\n%s", state)
        else:
            logger.warning("Состояние не получено")
            return 1

        # modem.disconnect()  # ❌ НЕ ОТКЛЮЧАЕМСЯ
        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1