"""
CLI команды для работы с портом конфигурации модема.
"""

import logging
import time

from modem_test_platform.devices.modem.adapter.serial_adapter.serial_adapter import SerialAdapter
from modem_test_platform.protocols.serial_protocol.serial_protocol import SerialProtocol
from modem_test_platform.protocols.serial_protocol.serial_transport import SerialTransport
logger = logging.getLogger(__name__)


def get_modem(port: str, baudrate: int = 115200, timeout: float = 0.5) -> SerialAdapter:
    """Создать и вернуть адаптер модема для порта конфигурации."""
    transport = SerialTransport(port=port, baudrate=baudrate, timeout=timeout)
    protocol = SerialProtocol(transport)
    modem = SerialAdapter(protocol)
    return modem


def _get_modem_from_state():
    """Получить модем из состояния."""
    from modem_test_platform.cli.session_state import state
    return state.modem


def configure_modem(args) -> int:
    """Команда: проверить подключение к модему и прочитать конфигурацию."""
    try:
        from modem_test_platform.cli.session_state import state

        if state.modem is None:
            state.modem = get_modem(args.port)
            state.port = args.port

        if not state.modem.protocol.transport.is_open:
            state.modem.connect()

        logger.info("Чтение конфигурации...")
        config = state.modem.read_configuration()
        if config:
            logger.info("Конфигурация получена")
            state.update_from_config(config)
        else:
            logger.warning("Конфигурация не получена")
            return 1

        logger.info("Чтение состояния канала...")
        link_state = state.modem.read_link_state()
        if link_state:
            logger.info("Состояние получено")
            state.update_from_link_state(link_state)
        else:
            logger.warning("Состояние не получено")

        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def read_config_cmd(args) -> int:
    """Команда: чтение конфигурации."""
    try:
        from modem_test_platform.cli.session_state import state

        if state.modem is None or not state.modem.protocol.transport.is_open:
            logger.error("Модем не подключен")
            return 1

        logger.info("Чтение конфигурации...")
        config = state.modem.read_configuration()

        if config:
            logger.info("Конфигурация:\n%s", config)
            state.update_from_config(config)
        else:
            logger.warning("Конфигурация не получена")
            return 1

        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def read_stat_cmd(args) -> int:
    """Команда: чтение состояния канала."""
    try:
        from modem_test_platform.cli.session_state import state

        if state.modem is None or not state.modem.protocol.transport.is_open:
            logger.error("Модем не подключен")
            return 1

        logger.info("Чтение состояния канала...")
        link_state = state.modem.read_link_state()

        if link_state:
            logger.info("Состояние:\n%s", link_state)
            state.update_from_link_state(link_state)
        else:
            logger.warning("Состояние не получено")
            return 1

        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def set_frequency_cmd(args) -> int:
    """Команда: установка частоты."""
    try:
        from modem_test_platform.cli.session_state import state

        if state.modem is None or not state.modem.protocol.transport.is_open:
            logger.error("Модем не подключен")
            return 1

        logger.info("Установка частоты %d МГц...", args.frequency)
        result = state.modem.set_frequency(args.frequency)

        if result:
            logger.info("✅ Частота успешно установлена")
            config = state.modem.read_configuration()
            if config:
                state.update_from_config(config)
        else:
            logger.warning("⚠️ Не удалось установить частоту")
            return 1

        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def set_mode_cmd(args) -> int:
    """Команда: установка режима."""
    try:
        from modem_test_platform.cli.session_state import state

        if state.modem is None or not state.modem.protocol.transport.is_open:
            logger.error("Модем не подключен")
            return 1

        logger.info("Установка режима %s...", args.mode)
        result = state.modem.set_mode(args.mode)

        if result:
            logger.info("✅ Режим успешно установлен")
            config = state.modem.read_configuration()
            if config:
                state.update_from_config(config)
        else:
            logger.warning("⚠️ Не удалось установить режим")
            return 1

        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def toggle_led_cmd(args) -> int:
    """Команда: переключение LED."""
    try:
        from modem_test_platform.cli.session_state import state

        if state.modem is None or not state.modem.protocol.transport.is_open:
            logger.error("Модем не подключен")
            return 1

        logger.info("Переключение LED...")
        result = state.modem.toggle_led()

        if result:
            logger.info("✅ LED переключен")
            config = state.modem.read_configuration()
            if config:
                state.update_from_config(config)
        else:
            logger.warning("⚠️ Не удалось переключить LED")
            return 1

        return 0

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1


def reboot_cmd(args) -> int:
    """Команда: перезагрузка модема."""
    try:
        from modem_test_platform.cli.session_state import state

        if state.modem is None or not state.modem.protocol.transport.is_open:
            logger.error("Модем не подключен")
            return 1

        logger.info("Перезагрузка модема...")
        result = state.modem.reboot()

        if result:
            logger.info("✅ Модем перезагружен")
            # После ребута читаем конфигурацию
            time.sleep(0.5)
            config = state.modem.read_configuration()
            if config:
                state.update_from_config(config)
            return 0
        else:
            logger.warning("⚠️ Не удалось перезагрузить модем")
            return 1

    except Exception as e:
        logger.error("Ошибка: %s", e)
        return 1