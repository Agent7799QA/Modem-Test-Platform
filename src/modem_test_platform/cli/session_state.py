"""
Состояние сессии для CLI меню.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modem_test_platform.devices.modem.adapter.serial_adapter.serial_adapter import SerialAdapter
from modem_test_platform.devices.modem.modemconfiguration import ModemConfiguration

# ✅ Глобальный объект состояния
state: Optional['SessionState'] = None


@dataclass
class SessionState:
    """Состояние сессии CLI."""

    # Подключение
    port: str = ""
    modem: Optional[SerialAdapter] = None
    is_connected: bool = False

    # Параметры из print
    device_type: Optional[str] = None       # RX/TX
    version: Optional[str] = None
    serial_number: Optional[str] = None
    mode: Optional[str] = None              # Long range / swarm+ / swarm
    frequency: Optional[int] = None         # 3500/4000/4500/6500
    link_rate: Optional[int] = None         # 5/10/25/40/50
    protocol: Optional[str] = None          # crsf/sbus/mavlink/raw
    fhss: Optional[int] = None              # 0-4
    dsss: Optional[int] = None              # 0-7
    network_address: Optional[int] = None   # PAN
    bind_address: Optional[int] = None      # BIND
    attenuation: Optional[int] = None       # 0-30
    led_state: Optional[bool] = None        # ON/OFF

    # Состояние канала (stat)
    uplink_lq: Optional[int] = None
    uplink_rssi: Optional[int] = None
    downlink_lq: Optional[int] = None
    downlink_rssi: Optional[int] = None

    # Время последних операций
    last_config_time: Optional[str] = None
    last_stat_time: Optional[str] = None
    last_command_time: Optional[str] = None
    last_reboot_time: Optional[str] = None

    # Телеметрия
    monitor_active: bool = False
    monitor_lq: Optional[int] = None
    monitor_rssi: Optional[int] = None
    stats_count: int = 0
    emulation_active: bool = False
    emulation_freq: float = 0.0

    # dual connection
    dual_connected: bool = False
    dual_tx_port: Optional[str] = None
    dual_rx_port: Optional[str] = None

    def update_from_config(self, config: ModemConfiguration) -> None:
        """Обновить состояние из конфигурации."""
        if config.device_type:
            self.device_type = config.device_type
        if config.version:
            self.version = config.version
        if config.serial_number:
            self.serial_number = config.serial_number
        if config.mode:
            self.mode = config.mode
        if config.frequency is not None:
            self.frequency = config.frequency
        if config.link_rate is not None:
            self.link_rate = config.link_rate
        if config.protocol:
            self.protocol = config.protocol
        if config.fhss is not None:
            self.fhss = config.fhss
        if config.dsss is not None:
            self.dsss = config.dsss
        if config.network_address is not None:
            self.network_address = config.network_address
        if config.bind_address is not None:
            self.bind_address = config.bind_address
        if config.attenuation is not None:
            self.attenuation = config.attenuation
        if config.led_state is not None:
            self.led_state = config.led_state

        self.last_config_time = datetime.now().strftime("%H:%M:%S")
        self.is_connected = True

    def update_from_link_state(self, link_state) -> None:
        """Обновить состояние из состояния канала."""
        if link_state:
            self.uplink_lq = link_state.uplink_lq
            self.uplink_rssi = link_state.uplink_rssi
            self.downlink_lq = link_state.downlink_lq
            self.downlink_rssi = link_state.downlink_rssi
            self.last_stat_time = datetime.now().strftime("%H:%M:%S")

    def get_connection_status(self) -> str:
        """Получить статус подключения."""
        if self.is_connected and self.modem:
            device = f" ({self.device_type})" if self.device_type else ""
            return f"🟢 Подключен{device}"
        return "🔴 Отключен"

    def get_frequency_display(self) -> str:
        """Получить отображение частоты."""
        if self.frequency is not None:
            return f"{self.frequency} МГц"
        return "—"

    def get_mode_display(self) -> str:
        """Получить отображение режима."""
        return self.mode if self.mode else "—"

    def get_led_display(self) -> str:
        """Получить отображение LED."""
        if self.led_state is True:
            return "🟢 ON"
        elif self.led_state is False:
            return "🔴 OFF"
        return "—"

    def get_rate_display(self) -> str:
        """Получить отображение скорости."""
        if self.link_rate is not None:
            return f"{self.link_rate} Гц"
        return "—"

    def get_protocol_display(self) -> str:
        """Получить отображение протокола."""
        return self.protocol if self.protocol else "—"

    def get_fhss_display(self) -> str:
        """Получить отображение FHSS."""
        if self.fhss is not None:
            return str(self.fhss)
        return "—"

    def get_dsss_display(self) -> str:
        """Получить отображение DSSS."""
        if self.dsss is not None:
            return str(self.dsss)
        return "—"

    def get_pan_display(self) -> str:
        """Получить отображение PAN."""
        if self.network_address is not None:
            return str(self.network_address)
        return "—"

    def get_bind_display(self) -> str:
        """Получить отображение BIND."""
        if self.bind_address is not None:
            return str(self.bind_address)
        return "—"

    def get_stat_display(self) -> str:
        """Получить отображение состояния канала."""
        if self.uplink_lq is not None and self.uplink_rssi is not None:
            return f"LQ: {self.uplink_lq}% 📶 RSSI: {self.uplink_rssi} dBm"
        return "Нет данных"

    def get_config_time_display(self) -> str:
        """Получить отображение времени чтения конфигурации."""
        if self.last_config_time:
            return f"✅ Выполнено ({self.last_config_time})"
        return "⏹ Не выполнялась"

    def get_stat_time_display(self) -> str:
        """Получить отображение времени чтения состояния."""
        if self.last_stat_time:
            return f"✅ Выполнено ({self.last_stat_time})"
        return "⏹ Не выполнялась"

    def get_reboot_display(self) -> str:
        """Отображение времени последней перезагрузки."""
        if self.last_reboot_time:
            return f"🔄 {self.last_reboot_time}"
        return "⏹ Не выполнялась"

    def get_monitor_display(self) -> str:
        """Получить отображение статуса мониторинга."""
        if self.monitor_active:
            if self.monitor_lq is not None:
                return f"📡 Активен (LQ: {self.monitor_lq}%)"
            return "📡 Активен"
        return "⏹ Остановлен"

    def get_stats_display(self) -> str:
        """Получить отображение статуса сбора статистики."""
        if self.stats_count > 0:
            return f"📊 {self.stats_count} измерений"
        return "📊 0 измерений"

    def get_emulation_display(self) -> str:
        """Получить отображение статуса эмуляции."""
        if self.emulation_active:
            return f"🎮 Активна ({self.emulation_freq:.0f} Гц)"
        return "⏹ Остановлена"

    def get_dual_status(self) -> str:
        """Получить статус подключения двух модемов."""
        if self.dual_connected:
            return f"🟢 TX:{self.dual_tx_port} RX:{self.dual_rx_port}"
        return "🔴 Не подключены"


# ✅ Инициализация глобального состояния
def get_state() -> SessionState:
    """Получить глобальное состояние сессии."""
    global state
    if state is None:
        state = SessionState()
    return state


def set_state(new_state: SessionState) -> None:
    """Установить глобальное состояние сессии."""
    global state
    state = new_state