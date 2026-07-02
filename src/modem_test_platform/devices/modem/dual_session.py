"""
Сессия для работы с двумя модемами (TX и RX).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List

from modem_test_platform.devices.modem.adapter.serial_adapter.port_scanner import (
    ModemInfo,
    find_tx_rx,
    scan_ports,
)
from modem_test_platform.devices.modem.adapter.serial_adapter.serial_adapter import SerialAdapter
from modem_test_platform.devices.modem.modemconfiguration import ModemConfiguration
from serial_transport import SerialTransport


@dataclass
class ModemPair:
    """Пара модемов TX и RX."""

    tx_port: str
    rx_port: str
    tx_adapter: Optional[SerialAdapter] = None
    rx_adapter: Optional[SerialAdapter] = None
    tx_info: Optional[ModemInfo] = None
    rx_info: Optional[ModemInfo] = None
    tx_config: Optional[ModemConfiguration] = None
    rx_config: Optional[ModemConfiguration] = None
    is_connected: bool = False


class DualModemSession:
    """
    Сессия для одновременной работы с TX и RX модемами.

    Управляет:
    - Сканированием портов
    - Подключением к обоим модемам
    - Чтением конфигураций
    - Синхронизацией
    """

    def __init__(self, baudrate: int = 115200):
        self.baudrate = baudrate
        self.pair: Optional[ModemPair] = None
        self._connected = False

    def scan(self) -> List[ModemInfo]:
        """Сканировать порты и найти модемы."""
        return scan_ports(self.baudrate)

    def connect(
        self, tx_port: Optional[str] = None, rx_port: Optional[str] = None
    ) -> Tuple[bool, Optional[ModemPair]]:
        """
        Подключиться к модемам.

        Args:
            tx_port: Порт TX (если None - автоопределение)
            rx_port: Порт RX (если None - автоопределение)

        Returns:
            Tuple[bool, Optional[ModemPair]]: (успех, пара модемов)
        """
        print("\n" + "=" * 60)
        print("   ПОДКЛЮЧЕНИЕ К МОДЕМАМ")
        print("=" * 60)

        # Если порты не указаны - сканируем
        if tx_port is None or rx_port is None:
            modems = self.scan()
            tx, rx = find_tx_rx(modems)

            if tx:
                tx_port = tx.port
            if rx:
                rx_port = rx.port

        if not tx_port or not rx_port:
            print("\n❌ Не удалось определить порты TX и RX")
            return False, None

        print(f"\n📌 Используемые порты:")
        print(f"   TX: {tx_port}")
        print(f"   RX: {rx_port}")

        try:
            # Создаем адаптеры
            tx_transport = SerialTransport(port=tx_port, baudrate=self.baudrate)
            rx_transport = SerialTransport(port=rx_port, baudrate=self.baudrate)

            tx_adapter = SerialAdapter(tx_transport)
            rx_adapter = SerialAdapter(rx_transport)

            # Подключаемся
            tx_adapter.connect()
            rx_adapter.connect()

            # Читаем конфигурации
            tx_config = tx_adapter.read_configuration()
            rx_config = rx_adapter.read_configuration()

            # Создаем пару
            self.pair = ModemPair(
                tx_port=tx_port,
                rx_port=rx_port,
                tx_adapter=tx_adapter,
                rx_adapter=rx_adapter,
                tx_config=tx_config,
                rx_config=rx_config,
                is_connected=True,
            )

            self._connected = True

            print(f"\n✅ Подключено:")
            print(f"   TX: {tx_port} ({tx_config.device_type if tx_config else 'unknown'})")
            print(f"   RX: {rx_port} ({rx_config.device_type if rx_config else 'unknown'})")

            return True, self.pair

        except Exception as e:
            print(f"\n❌ Ошибка подключения: {e}")
            return False, None

    def disconnect(self) -> None:
        """Отключить все модемы."""
        if self.pair:
            if self.pair.tx_adapter:
                try:
                    self.pair.tx_adapter.disconnect()
                except:
                    pass
            if self.pair.rx_adapter:
                try:
                    self.pair.rx_adapter.disconnect()
                except:
                    pass
        self._connected = False
        print("\n✅ Модемы отключены")

    def is_connected(self) -> bool:
        """Проверить, подключены ли модемы."""
        return self._connected and self.pair is not None

    def get_pair(self) -> Optional[ModemPair]:
        """Получить пару модемов."""
        return self.pair

    def read_configs(self) -> Tuple[Optional[ModemConfiguration], Optional[ModemConfiguration]]:
        """Перечитать конфигурации обоих модемов."""
        if not self.is_connected():
            print("❌ Модемы не подключены")
            return None, None

        try:
            tx_config = self.pair.tx_adapter.read_configuration()
            rx_config = self.pair.rx_adapter.read_configuration()

            self.pair.tx_config = tx_config
            self.pair.rx_config = rx_config

            return tx_config, rx_config

        except Exception as e:
            print(f"❌ Ошибка чтения конфигураций: {e}")
            return None, None
