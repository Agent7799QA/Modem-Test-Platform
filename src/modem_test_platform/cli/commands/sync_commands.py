"""
CLI команды для работы с двумя модемами (TX/RX).
"""

import logging
from typing import Optional

from modem_test_platform.cli.session_state import state


from modem_test_platform.devices.modem.adapter.serial_adapter.port_scanner import print_modems
from modem_test_platform.devices.modem.dual_session import DualModemSession
from modem_test_platform.devices.modem.synchronizer import ModemSynchronizer
from modem_test_platform.devices.modem.verifier import ModemVerifier

logger = logging.getLogger(__name__)

# Глобальная сессия для двух модемов
dual_session: Optional[DualModemSession] = None


def get_dual_session() -> Optional[DualModemSession]:
    """Получить или создать сессию для двух модемов."""
    global dual_session
    if dual_session is None:
        dual_session = DualModemSession()
    return dual_session


def cmd_scan_ports() -> int:
    """Сканировать порты и найти модемы."""
    print("\n" + "=" * 60)
    print("   СКАНИРОВАНИЕ ПОРТОВ")
    print("=" * 60)

    session = get_dual_session()
    modems = session.scan()

    if modems:
        print_modems(modems)
        print(f"\n✅ Найдено модемов: {len(modems)}")
    else:
        print("\n❌ Модемы не найдены")

    return 0


def cmd_connect_dual() -> int:
    """Подключиться к двум модемам."""
    session = get_dual_session()
    success, pair = session.connect()

    if success and pair:
        # Обновляем глобальное состояние
        if pair.tx_config:
            state.device_type = pair.tx_config.device_type
            state.version = pair.tx_config.version
            state.serial_number = pair.tx_config.serial_number
            state.mode = pair.tx_config.mode
            state.frequency = pair.tx_config.frequency
            state.link_rate = pair.tx_config.link_rate
            state.protocol = pair.tx_config.protocol
            state.fhss = pair.tx_config.fhss
            state.dsss = pair.tx_config.dsss
            state.network_address = pair.tx_config.network_address
            state.bind_address = pair.tx_config.bind_address
            state.attenuation = pair.tx_config.attenuation
            state.led_state = pair.tx_config.led_state

        return 0
    else:
        return 1


def cmd_disconnect_dual() -> int:
    """Отключить все модемы."""
    session = get_dual_session()
    session.disconnect()
    return 0


def cmd_sync_modems() -> int:
    """Синхронизировать RX по TX."""
    session = get_dual_session()

    if not session.is_connected():
        print("❌ Модемы не подключены. Сначала выполните 'Подключиться к двум модемам'")
        return 1

    pair = session.get_pair()
    success, results = ModemSynchronizer.sync(pair.tx_adapter, pair.rx_adapter)

    if success:
        # Обновляем конфигурацию RX
        session.read_configs()
        return 0
    else:
        return 1


def cmd_verify_link() -> int:
    """Проверить связь между модемами."""
    session = get_dual_session()

    if not session.is_connected():
        print("❌ Модемы не подключены. Сначала выполните 'Подключиться к двум модемам'")
        return 1

    pair = session.get_pair()
    results = ModemVerifier.ping(pair.tx_adapter, pair.rx_adapter, count=10)

    return 0 if results["summary"]["status"] in ["excellent", "good"] else 1
