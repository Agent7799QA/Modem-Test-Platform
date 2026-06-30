from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Configuration:
    """Конфигурация модема, получаемая по команде print."""

    # Device section
    device_type: Optional[str] = None  # "RX" или "TX"
    version: Optional[str] = None
    serial_number: Optional[str] = None
    led_state: Optional[bool] = None  # Состояние светодиода (ON/OFF)

    # Radio section
    mode: Optional[str] = None  # "Long range", "swarm", "swarm+"
    link_rate: Optional[int] = None  # 5, 10, 25, 40, 50 Hz
    frequency: Optional[int] = None  # 3500, 4000, 4500, 6500 MHz
    channel_code: Optional[int] = None  # 1-24
    attenuation: Optional[int] = None  # 0-30 dB
    module_address: Optional[int] = None  # 0-65534
    network_address: Optional[int] = None  # 0-65534 (PAN)
    bind_address: Optional[int] = None  # 0-65534
    crystal_trim: Optional[int] = None  # Калибровка (не трогать)
    fhss: Optional[int] = None  # 0-4
    dsss: Optional[int] = None  # 0-7 (только 0-3 рабочие)
    time_slotting: Optional[bool] = None  # Временное деление
    retransmissions: Optional[bool] = None  # Ретрансляции (TTL)
    acknowledge: Optional[bool] = None  # Подтверждения
    max_clients: Optional[int] = None  # Максимум клиентов
    ew_tests: Optional[bool] = None  # Режим РЭБ тестов

    # Serial section
    baudrate: Optional[int] = None
    parity: Optional[str] = None  # "none", "even", "odd"
    stop_bits: Optional[int] = None  # 1 или 2
    inverted: Optional[bool] = None  # Инверсия сигнала

    # Protocol section
    protocol: Optional[str] = None  # "crsf", "sbus", "mavlink", "raw"
    preset: Optional[str] = None  # "default", "froglr", "frogsw", "frogsw+"

    # External interface section
    ext_mode: Optional[str] = None  # "off", "bk", "drop", "rssi"
    pin_0_mode: Optional[str] = None  # "off", "pwm", "servo", "mg90s", "syncout", "debug"
    pin_0_dependency: Optional[int] = None  # 1-70 (AUX channel, pitch, roll, altitude)
    pin_1_mode: Optional[str] = None
    pin_1_dependency: Optional[int] = None

    # Raw ответ от модема
    raw: Optional[str] = None