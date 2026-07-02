"""
Сканер портов для обнаружения модемов Салангана-К3
Адаптирован из modem_tester-master
"""
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import serial.tools.list_ports


from modem_test_platform.protocols.serial_protocol.exceptions import TransportConnectionError
from modem_test_platform.devices.modem.adapter.serial_adapter.serial_adapter import SerialAdapter
from modem_test_platform.devices.modem.modemconfiguration import ModemConfiguration
from modem_test_platform.protocols.serial_protocol.serial_transport import SerialTransport

logger = logging.getLogger(__name__)

@dataclass
class ModemInfo:
    """Информация о найденном модеме."""


    port: str
    port_type: str  # "TX" или "RX"
    config: Optional[ModemConfiguration] = None
    version: Optional[str] = None
    serial_number: Optional[str] = None
    is_connected: bool = False

    def to_dict(self) -> Dict:
        """Преобразовать в словарь."""
        result = {
            "port": self.port,
            "type": self.port_type,
            "version": self.version,
            "sn": self.serial_number,
            "connected": self.is_connected,
        }
        if self.config:
            result["config"] = self.config.to_dict() if hasattr(self.config, "to_dict") else {}
        return result


def scan_ports(baudrate: int = 115200, timeout: float = 0.1) -> List[ModemInfo]:
    """
    Найти все модемы на COM-портах.

    Args:
        baudrate: Скорость для сканирования
        timeout: Таймаут на порт

    Returns:
        List[ModemInfo]: Список найденных модемов
    """
    print("\n🔍 Сканирование COM-портов...")

    logger = logging.getLogger(__name__)

    result = []
    ports = [p.device for p in serial.tools.list_ports.comports()]

    if not ports:
        print("   ❌ COM-порты не найдены")
        return result

    print(f"   Найдено портов: {len(ports)}")

    for port in ports:
        info = _scan_port(port, baudrate, timeout)
        if info:
            result.append(info)
            print(f"   {port}  → ✅ {info.port_type}")
            logger.info(f"✅ Найден модем на {port}: {info.port_type}")
        else:
            print(f"   {port}  → ❌ Не модем")
            logger.debug(f"❌ На {port} модем не найден")
    return result


def _scan_port(port: str, baudrate: int, timeout: float) -> Optional[ModemInfo]:
    """Сканировать один порт."""
    adapter = None
    logger.debug(f"Сканирование {port} (baudrate={baudrate}, timeout={timeout})")
    try:
        transport = SerialTransport(port=port, baudrate=baudrate, timeout=timeout)
        adapter = SerialAdapter(transport)

        # Подключаемся
        adapter.connect()

        # 1. Отправляем help для проверки
        try:
            response = adapter.send_command("help", timeout=timeout)
        except Exception:
            adapter.disconnect()
            return None

        # 2. Проверяем, что это модем
        is_tx = "Drone RC (TX)" in response
        is_rx = "Drone RC (RX)" in response

        if not is_tx and not is_rx:
            adapter.disconnect()
            return None

        port_type = "TX" if is_tx else "RX"

        # 3. Извлекаем версию и SN
        version = _extract_version(response)
        serial_number = _extract_serial(response)

        # 4. Читаем конфигурацию
        config = adapter.read_configuration()

        adapter.disconnect()

        return ModemInfo(
            port=port,
            port_type=port_type,
            config=config,
            version=version,
            serial_number=serial_number,
            is_connected=True,
        )

    except (TransportConnectionError, Exception):
        if adapter:
            try:
                adapter.disconnect()
            except:
                pass
        return None


def _extract_version(response: str) -> Optional[str]:
    """Извлечь версию прошивки."""
    match = re.search(r"Version:\s*([\d.]+)", response)
    return match.group(1) if match else None


def _extract_serial(response: str) -> Optional[str]:
    """Извлечь серийный номер."""
    match = re.search(r"SN:\s*(?:\.\.\s*)?([a-fA-F0-9]{16})", response, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r"([a-fA-F0-9]{16})", response)
    return match.group(1) if match else None


def find_tx_rx(modems: List[ModemInfo]) -> Tuple[Optional[ModemInfo], Optional[ModemInfo]]:
    """Найти TX и RX из списка."""
    tx = None
    rx = None
    for m in modems:
        if m.port_type == "TX":
            tx = m
        elif m.port_type == "RX":
            rx = m
    return tx, rx


def print_modems(modems: List[ModemInfo]) -> None:
    """Красиво вывести результаты сканирования."""
    if not modems:
        print("\n❌ Модемы не найдены")
        return

    print("\n" + "=" * 60)
    print("   РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ")
    print("=" * 60)

    for info in modems:
        print(f"\n📌 Порт: {info.port}  → ✅ {info.port_type}")
        if info.version:
            print(f"   Версия: {info.version}")
        if info.serial_number:
            print(f"   SN: {info.serial_number}")
        if info.config:
            # Исправлены имена полей
            params = []
            for key in ["frequency", "channel_code", "link_rate", "module_address", "bind_address"]:
                val = getattr(info.config, key, None)
                if val is not None:
                    # Для красивого вывода используем сокращённые имена
                    display_key = {
                        "frequency": "freq",
                        "channel_code": "code",
                        "link_rate": "rate",
                        "module_address": "address",
                        "bind_address": "bind",
                    }.get(key, key)
                    params.append(f"{display_key}={val}")
            if params:
                print(f"   Параметры: {', '.join(params)}")