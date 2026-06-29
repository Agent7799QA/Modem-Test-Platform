from dataclasses import dataclass


@dataclass(slots=True)
class Configuration:

    # Device
    device_type: str | None = None       # RX / TX
    version: str | None = None
    serial_number: str | None = None

    # Protocol
    protocol: str | None = None
    preset: str | None = None

    # Radio
    mode: str | None = None
    link_rate: int | None = None
    frequency: int | None = None
    channel_code: int | None = None
    attenuation: int | None = None

    module_address: int | None = None
    network_address: int | None = None
    bind_address: int | None = None

    crystal_trim: int | None = None

    fhss: int | None = None
    dsss: int | None = None

    # TX only
    retransmissions: bool | None = None
    acknowledge: bool | None = None
    max_clients: int | None = None
    time_slotting: bool | None = None

    # RX only
    ew_tests: bool | None = None

    # Serial

    baudrate: int | None = None
    parity: str | None = None
    stop_bits: int | None = None

    raw: str = ""