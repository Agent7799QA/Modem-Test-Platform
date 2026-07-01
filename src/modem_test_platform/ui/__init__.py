"""
UI модули для отображения данных.
"""

from modem_test_platform.ui.rich_utils import (
    console,
    format_rssi,
    format_lq,
    format_status,
    create_telemetry_table,
    create_dashboard,
    create_progress_bar,
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
)
from modem_test_platform.ui.rich_dashboard import (
    TelemetryDashboard,
    SimpleMonitorDisplay,
)

__all__ = [
    "console",
    "format_rssi",
    "format_lq",
    "format_status",
    "create_telemetry_table",
    "create_dashboard",
    "create_progress_bar",
    "print_header",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "TelemetryDashboard",
    "SimpleMonitorDisplay",
]