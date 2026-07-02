"""
CLI команды для управления модемом и телеметрией.
"""

# Импорты из config_commands
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

# Импорты из telemetry_commands
from modem_test_platform.cli.commands.telemetry_commands import (
    TelemetryCli,
    TelemetryCliConfig,
    parse_channels,
    add_telemetry_parser,
)

# Импорты из sync_commands
from modem_test_platform.cli.commands.sync_commands import (
    cmd_scan_ports,
    cmd_connect_dual,
    cmd_sync_modems,
    cmd_verify_link,
    cmd_disconnect_dual,
)

__all__ = [
    # config_commands
    "get_modem",
    "configure_modem",
    "set_frequency_cmd",
    "set_mode_cmd",
    "toggle_led_cmd",
    "reboot_cmd",
    "read_config_cmd",
    "read_stat_cmd",
    # telemetry_commands
    "TelemetryCli",
    "TelemetryCliConfig",
    "parse_channels",
    "add_telemetry_parser",
    # sync_commands
    "cmd_scan_ports",
    "cmd_connect_dual",
    "cmd_sync_modems",
    "cmd_verify_link",
    "cmd_disconnect_dual",
]