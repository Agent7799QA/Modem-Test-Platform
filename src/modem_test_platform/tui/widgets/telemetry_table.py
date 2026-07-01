"""
Виджет таблицы телеметрии
"""

from textual.widgets import DataTable
from textual.reactive import reactive
from rich.text import Text

from modem_test_platform.monitoring.rx_monitor import LinkState


class TelemetryTable(DataTable):
    """Таблица для отображения телеметрии в реальном времени"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_columns("Параметр", "Значение")
        self.add_rows([
            ("📶 Uplink LQ", "N/A"),
            ("📡 Uplink RSSI", "N/A"),
            ("📶 Downlink LQ", "N/A"),
            ("📡 Downlink RSSI", "N/A"),
            ("📊 Измерений", "0"),
            ("⏱️ Длительность", "0с"),
        ])
        self._row_map = {
            "uplink_lq": 0,
            "uplink_rssi": 1,
            "downlink_lq": 2,
            "downlink_rssi": 3,
            "count": 4,
            "duration": 5,
        }

    def update(self, link: LinkState, count: int = 0, duration: float = 0.0) -> None:
        """Обновить данные в таблице"""

        # Цвет для LQ
        def format_lq(value: int) -> str:
            if value >= 90:
                return f"[green]{value}%[/green]"
            elif value >= 60:
                return f"[yellow]{value}%[/yellow]"
            else:
                return f"[red]{value}%[/red]"

        # Цвет для RSSI
        def format_rssi(value: int) -> str:
            if value >= -60:
                return f"[green]{value} dBm[/green]"
            elif value >= -80:
                return f"[yellow]{value} dBm[/yellow]"
            elif value >= -100:
                return f"[orange1]{value} dBm[/orange1]"
            else:
                return f"[red]{value} dBm[/red]"

        # Обновляем строки
        self.update_cell(self._row_map["uplink_lq"], 1, format_lq(link.uplink_lq))
        self.update_cell(self._row_map["uplink_rssi"], 1, format_rssi(link.uplink_rssi))
        self.update_cell(self._row_map["downlink_lq"], 1, format_lq(link.downlink_lq))
        self.update_cell(self._row_map["downlink_rssi"], 1, format_rssi(link.downlink_rssi))
        self.update_cell(self._row_map["count"], 1, f"{count}")
        self.update_cell(self._row_map["duration"], 1, f"{duration:.1f}с")