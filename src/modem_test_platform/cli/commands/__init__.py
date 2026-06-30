"""
CLI команды для управления модемом и телеметрией.
"""

from modem_test_platform.cli.commands.telemetry_commands import (
    TelemetryCli,
    TelemetryCliConfig,
    parse_channels,
    add_telemetry_parser,
)

# Экспортируем все функции для добавления парсеров
__all__ = [
    "TelemetryCli",
    "TelemetryCliConfig",
    "parse_channels",
    "add_telemetry_parser",
]