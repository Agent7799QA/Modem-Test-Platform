"""
Эмуляция команд через CRSF протокол.
"""

from modem_test_platform.emulation.command_emulator import (
    CommandEmulator,
    CommandEmulatorWithCallback,
    EmulationConfig,
    create_default_channels,
    create_channels_from_pwm,
)