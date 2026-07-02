"""
CLI команды для работы с двумя модемами (TX/RX).
"""

import logging

from modem_test_platform.cli.session_state import get_state
from modem_test_platform.devices.modem.adapter.serial_adapter.port_scanner import (
    ModemInfo,
    find_tx_rx,
    print_modems,
    scan_ports,
)
from modem_test_platform.devices.modem.adapter.serial_adapter.serial_adapter import SerialAdapter
from modem_test_platform.devices.modem.modemconfiguration import ModemConfiguration
from modem_test_platform.devices.modem.synchronizer import ModemSynchronizer
from modem_test_platform.devices.modem.verifier import ModemVerifier
from modem_test_platform.protocols.serial_protocol.serial_transport import SerialTransport

logger = logging.getLogger(__name__)

# Получаем глобальное состояние
state = get_state()


def _create_adapter(port: str) -> SerialAdapter:
    """Создать адаптер для порта."""
    transport = SerialTransport(port=port, baudrate=115200, timeout=0.1)
    return SerialAdapter(transport)


def cmd_scan_ports() -> int:
    """Сканировать порты и найти модемы."""
    print("\n" + "=" * 60)
    print("   СКАНИРОВАНИЕ ПОРТОВ")
    print("=" * 60)

    modems = scan_ports()

    if modems:
        print_modems(modems)
        print(f"\n✅ Найдено модемов: {len(modems)}")
    else:
        print("\n❌ Модемы не найдены")

    return 0


def cmd_connect_dual() -> int:
    """Подключиться к двум модемам (автоматическое определение TX/RX)."""
    print("\n" + "=" * 60)
    print("   ПОДКЛЮЧЕНИЕ К ДВУМ МОДЕМАМ")
    print("=" * 60)

    # Если уже подключены — отключаем
    if state.dual_connected:
        print("⚠️ Модемы уже подключены. Сначала отключите их (пункт 21).")
        return 1

    # Сканируем порты
    modems = scan_ports()
    if not modems:
        print("\n❌ Модемы не найдены")
        return 1

    # Находим TX и RX
    tx_info, rx_info = find_tx_rx(modems)

    if not tx_info or not rx_info:
        print("\n❌ Не удалось найти одновременно TX и RX модемы")
        if tx_info:
            print(f"   Найден TX: {tx_info.port}")
        else:
            print("   TX не найден")
        if rx_info:
            print(f"   Найден RX: {rx_info.port}")
        else:
            print("   RX не найден")
        return 1

    print(f"\n📌 Обнаружены:")
    print(f"   TX: {tx_info.port} (SN: {tx_info.serial_number})")
    print(f"   RX: {rx_info.port} (SN: {rx_info.serial_number})")

    # Создаём адаптеры
    tx_adapter = _create_adapter(tx_info.port)
    rx_adapter = _create_adapter(rx_info.port)

    try:
        print("\n🔌 Подключение...")
        tx_adapter.connect()
        rx_adapter.connect()

        # Читаем конфигурации
        tx_config = tx_adapter.read_configuration()
        rx_config = rx_adapter.read_configuration()

        # Сохраняем в состояние
        state.dual_connected = True
        state.dual_tx_port = tx_info.port
        state.dual_rx_port = rx_info.port
        state.tx_adapter = tx_adapter
        state.rx_adapter = rx_adapter
        state.tx_config = tx_config
        state.rx_config = rx_config

        # Обновляем также основное состояние (для отображения в меню)
        # Если пользователь захочет переключиться на работу с одним модемом,
        # он может использовать "Сменить порт" (пункт 16)
        state.device_type = "TX"  # или "RX"? пока оставим как есть
        state.version = tx_config.version if tx_config else None
        state.serial_number = tx_config.serial_number if tx_config else None
        state.mode = tx_config.mode if tx_config else None
        state.frequency = tx_config.frequency if tx_config else None
        state.link_rate = tx_config.link_rate if tx_config else None
        state.protocol = tx_config.protocol if tx_config else None
        state.fhss = tx_config.fhss if tx_config else None
        state.dsss = tx_config.dsss if tx_config else None
        state.network_address = tx_config.network_address if tx_config else None
        state.bind_address = tx_config.bind_address if tx_config else None
        state.attenuation = tx_config.attenuation if tx_config else None
        state.led_state = tx_config.led_state if tx_config else None

        print("\n✅ Подключение успешно!")
        print(f"   TX: {tx_info.port} (версия {tx_config.version if tx_config else '?'})")
        print(f"   RX: {rx_info.port} (версия {rx_config.version if rx_config else '?'})")
        print("\n   Теперь доступны команды синхронизации и проверки связи.")

        return 0

    except Exception as e:
        print(f"\n❌ Ошибка подключения: {e}")
        # Пытаемся отключить, если что-то уже подключилось
        try:
            tx_adapter.disconnect()
        except:
            pass
        try:
            rx_adapter.disconnect()
        except:
            pass
        state.dual_connected = False
        return 1


def cmd_disconnect_dual() -> int:
    """Отключить все модемы."""
    print("\n" + "=" * 60)
    print("   ОТКЛЮЧЕНИЕ МОДЕМОВ")
    print("=" * 60)

    if not state.dual_connected:
        print("ℹ️ Модемы не подключены")
        return 0

    try:
        if state.tx_adapter:
            state.tx_adapter.disconnect()
        if state.rx_adapter:
            state.rx_adapter.disconnect()
    except Exception as e:
        print(f"⚠️ Ошибка при отключении: {e}")

    state.dual_connected = False
    state.dual_tx_port = None
    state.dual_rx_port = None
    state.tx_adapter = None
    state.rx_adapter = None
    state.tx_config = None
    state.rx_config = None
    state.sync_status = None
    state.sync_params = None
    state.last_sync_time = None

    print("\n✅ Модемы отключены")
    return 0


def cmd_sync_modems() -> int:
    """Синхронизировать RX по TX."""
    print("\n" + "=" * 60)
    print("   СИНХРОНИЗАЦИЯ TX → RX")
    print("=" * 60)

    if not state.dual_connected:
        print("❌ Модемы не подключены. Сначала выполните 'Подключиться к двум модемам' (пункт 18)")
        return 1

    if not state.tx_adapter or not state.rx_adapter:
        print("❌ Адаптеры не инициализированы")
        return 1

    # Выполняем синхронизацию
    success, results = ModemSynchronizer.sync(state.tx_adapter, state.rx_adapter)

    # Обновляем состояние
    if success:
        state.sync_status = "synced"
        state.sync_params = ModemSynchronizer.SYNC_PARAMS
        state.last_sync_time = results.get("last_sync_time", None)

        # Перечитываем конфигурации
        try:
            state.tx_config = state.tx_adapter.read_configuration()
            state.rx_config = state.rx_adapter.read_configuration()
        except:
            pass

        print("\n✅ Синхронизация успешна!")
    else:
        state.sync_status = "partial"
        print("\n⚠️ Синхронизация неполная. Проверьте различия.")
        if results.get("errors"):
            for err in results["errors"]:
                print(f"   ❌ {err}")

    return 0 if success else 1


def cmd_verify_link() -> int:
    """Проверить связь между модемами."""
    print("\n" + "=" * 60)
    print("   ПРОВЕРКА СВЯЗИ")
    print("=" * 60)

    if not state.dual_connected:
        print("❌ Модемы не подключены. Сначала выполните 'Подключиться к двум модемам' (пункт 18)")
        return 1

    if not state.tx_adapter or not state.rx_adapter:
        print("❌ Адаптеры не инициализированы")
        return 1

    # Выполняем проверку
    results = ModemVerifier.ping(state.tx_adapter, state.rx_adapter, count=10)

    # Обновляем статистику в состоянии (по желанию)
    if results["summary"]["status"] in ["excellent", "good"]:
        return 0
    else:
        return 1