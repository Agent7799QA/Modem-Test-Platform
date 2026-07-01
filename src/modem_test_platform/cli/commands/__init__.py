"""
CLI команды для управления модемом и телеметрией.
"""

from modem_test_platform.cli.commands.config_commands import (
    get_modem,
    configure_modem,
    set_frequency_cmd,
    set_mode_cmd,
    toggle_led_cmd,
    reboot_cmd,
    read_config_cmd,
    read_stat_cmd,
)

from modem_test_platform.cli.commands.telemetry_commands import (
    TelemetryCli,
    TelemetryCliConfig,
    parse_channels,
    add_telemetry_parser,
)

__all__ = [
    "get_modem",
    "configure_modem",
    "set_frequency_cmd",
    "set_mode_cmd",
    "toggle_led_cmd",
    "reboot_cmd",
    "read_config_cmd",
    "read_stat_cmd",
    "TelemetryCli",
    "TelemetryCliConfig",
    "parse_channels",
    "add_telemetry_parser",
]