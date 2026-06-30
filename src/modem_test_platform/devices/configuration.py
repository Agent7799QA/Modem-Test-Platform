from dataclasses import dataclass, field


@dataclass
class Configuration:
    """Конфигурация модема."""

    # Сырой ответ
    raw: str = ""

    # ---------- Device ----------
    device_type: str | None = None          # "TX" или "RX"
    version: str | None = None              # версия прошивки
    serial_number: str | None = None        # серийный номер

    # ---------- Protocol ----------
    protocol: str | None = None             # crsf, sbus, mavlink, raw
    preset: str | None = None               # default, custom и т.д.

    # ---------- Radio (общие) ----------
    mode: str | None = None                 # longrange, swarm, swarm+, 100kbps
    link_rate: int | None = None            # 5, 10, 25, 40, 50 Гц
    frequency: int | None = None            # 3500, 4000, 4500, 6500 МГц
    channel_code: int | None = None         # 1-24
    attenuation: int | None = None          # 0-30 дБ
    module_address: int | None = None       # 0-65534
    network_address: int | None = None      # 0-65534
    bind_address: int | None = None         # 0-65534 (только для RX)
    crystal_trim: int | None = None         # 0-255
    fhss: int | None = None                 # 0-4
    dsss: int | None = None                 # 0-7

    # ---------- TX ----------
    time_slotting: bool | None = None       # True/False
    retransmissions: bool | None = None     # True/False
    acknowledge: bool | None = None         # True/False
    max_clients: int | None = None          # 1-8

    # ---------- RX ----------
    ew_tests: bool | None = None            # True/False

    # ---------- Serial ----------
    baudrate: int | None = None             # 57600, 100000, 115200, 400000, 420000
    parity: str | None = None               # none, even, odd
    stop_bits: int | None = None            # 1, 2
    inverted: bool = False                  # True/False

    # ---------- External Interface ----------
    ext_mode: str | None = None             # off, bk, drop, rssi
    pin_0_mode: str | None = None           # off, pwm, servo, mg90s, syncout, debug
    pin_0_dependency: int | None = None     # 1-70
    pin_1_mode: str | None = None           # off, pwm, servo, mg90s, syncout, debug
    pin_1_dependency: int | None = None     # 1-70