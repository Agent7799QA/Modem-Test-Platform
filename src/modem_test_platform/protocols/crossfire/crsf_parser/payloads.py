import logging

from construct import (
    Array,
    BitStruct,
    BitsInteger,
    ByteSwapped,
    Enum,
    Int16ub,
    Int24ub,
    Int8sb,
    Int8ub,
    Int32ub,
    Int16sb,
    FlagsEnum,
    GreedyBytes,
)
from construct.core import Struct
logger = logging.getLogger(__name__)

class PacketsTypes(Enum):
    GPS = 0x02
    VARIOS = 0x07
    BATTERY_SENSOR = 0x08
    BARO_ALTITUDE = 0x09
    HEARTBEAT = 0x0B
    VTX = 0x0F
    VTX_TEXT = 0x0E
    LINK_STATISTICS = 0x14
    RC_CHANNELS_PACKED = 0x16
    SUBSET_RC_CHANNELS_PACKED = 0x17
    LINK_STATISTICS_EXTENDED = 0x1C
    ATTITUDE = 0x1E
    FLIGHT_MODE = 0x21
    PING_DEVICES = 0x28
    DEVICE_INFO = 0x29
    REQUEST_SETTINGS = 0x2A
    PARAMETER_SETTINGS_ENTRY = 0x2B
    PARAMETER_READ = 0x2C
    PARAMETER_WRITE = 0x2D
    COMMAND = 0x32
    RADIO_ID = 0x3A
    OSD = 0x3B
    MSP_REQ = 0x7C
    MSP_RESP = 0x7D
    MSP_WRITE = 0x7E
    ARDUPILOT_RESP = 0x80


PAYLOADS_SIZE: "dict[int, int]" = {
    PacketsTypes.GPS: 15,
    PacketsTypes.VARIOS: 5,
    PacketsTypes.BATTERY_SENSOR: 8,
    PacketsTypes.BARO_ALTITUDE: 5,
    PacketsTypes.HEARTBEAT: 1,
    PacketsTypes.VTX: 6,
    PacketsTypes.VTX_TEXT: 58,
    PacketsTypes.LINK_STATISTICS: 10,
    PacketsTypes.RC_CHANNELS_PACKED: 22,
    PacketsTypes.SUBSET_RC_CHANNELS_PACKED: 7,
    PacketsTypes.LINK_STATISTICS_EXTENDED: 12,
    PacketsTypes.ATTITUDE: 6,
    PacketsTypes.FLIGHT_MODE: 0,
    PacketsTypes.PING_DEVICES: 2,
    PacketsTypes.DEVICE_INFO: 12,
    PacketsTypes.REQUEST_SETTINGS: 2,
    PacketsTypes.PARAMETER_SETTINGS_ENTRY: 0,
    PacketsTypes.PARAMETER_READ: 3,
    PacketsTypes.PARAMETER_WRITE: 0,
    PacketsTypes.COMMAND: 0,
    PacketsTypes.RADIO_ID: 6,
    PacketsTypes.OSD: 0,
    PacketsTypes.MSP_REQ: 0,
    PacketsTypes.MSP_RESP: 0,
    PacketsTypes.MSP_WRITE: 0,
    PacketsTypes.ARDUPILOT_RESP: 0,
}


# GPS packet structure
payload_gps = Struct(
    "origin_device_address" / Int8ub,
    "latitude" / Int32ub,  # degrees * 1e7
    "longitude" / Int32ub,  # degrees * 1e7
    "ground_speed" / Int16ub,  # km/h * 10
    "heading" / Int16ub,  # degrees * 100
    "altitude" / Int16ub,  # meters + 1000
    "satellites" / Int8ub,
)

# Vario sensor packet structure
payload_varios = Struct(
    "origin_device_address" / Int8ub,
    "vertical_speed" / Int16sb,  # cm/s
    "altitude" / Int16ub,  # meters + 1000
)

# Battery sensor packet structure
payload_battery_sensor = Struct(
    "voltage" / Int16ub,  # V * 100
    "current" / Int16ub,  # A * 100
    "capacity" / Int24ub,  # mAh
    "remaining" / Int8ub,  # percentage
)

# Barometric altitude packet structure
payload_baro_altitude = Struct(
    "origin_device_address" / Int8ub,
    "altitude" / Int32ub,  # cm
)

# Heartbeat packet structure
payload_heartbeat = Struct("origin_device_address" / Int8ub)

# Video transmitter packet structure
payload_vtx = Struct(
    "origin_device_address" / Int8ub,
    "band" / Enum(Int8ub, 
                 RACE_BAND=0,
                 BAND_A=1,
                 BAND_B=2,
                 BAND_E=3,
                 BAND_F=4,
                 BAND_D=5),
    "channel" / Int8ub,  # 1-8
    "power" / Enum(Int8ub,
                  POWER_0_MW=0,
                  POWER_1_MW=1,
                  POWER_2_MW=2,
                  POWER_10_MW=3,
                  POWER_25_MW=4,
                  POWER_100_MW=5,
                  POWER_200_MW=6,
                  POWER_500_MW=7,
                  POWER_1000_MW=8),
    "pitmode" / Enum(Int8ub, OFF=0, ON=1),
    "region" / Enum(Int8ub, INTERNATIONAL=0, USA=1),
)

# VTX Text packet structure
payload_vtx_text = Struct(
    "origin_device_address" / Int8ub,
    "text" / Array(57, Int8ub),  # VTX text message
)

# Link statistics packet structure
payload_link_statistics = Struct(
    "uplink_rssi_ant_1" / Int8ub,  # dBm
    "uplink_rssi_ant_2" / Int8ub,  # dBm
    "uplink_link_quality" / Int8ub,  # %
    "uplink_snr" / Int8sb,  # dB
    "diversity_active_antenna" / Enum(Int8ub, ANTENNA_1=0, ANTENNA_2=1),
    "rf_mode" / Enum(Int8ub, RF_4_FPS=0, RF_50_FPS=1, RF_150_FPS=2),
    "uplink_tx_power" / Enum(
        Int8ub,
        TX_POWER_0_MW=0,
        TX_POWER_10_MW=1,
        TX_POWER_25_MW=2,
        TX_POWER_100_MW=3,
        TX_POWER_500_MW=4,
        TX_POWER_1000_MW=5,
        TX_POWER_2000_MW=6,
    ),
    "downlink_rssi" / Int8ub,  # dBm
    "downlink_link_quality" / Int8ub,  # %
    "downlink_snr" / Int8sb,  # dB
)

# Extended Link statistics packet structure
payload_link_statistics_extended = Struct(
    "uplink_rssi_ant_1" / Int8ub,
    "uplink_rssi_ant_2" / Int8ub,
    "uplink_link_quality" / Int8ub,
    "uplink_snr" / Int8sb,
    "active_antenna" / Enum(Int8ub, ANTENNA_1=0, ANTENNA_2=1),
    "rf_mode" / Enum(Int8ub, RF_4_FPS=0, RF_50_FPS=1, RF_150_FPS=2),
    "uplink_tx_power" / Enum(Int8ub, _0_mW=0, _10_mW=1, _25_mW=2, _100_mW=3, _500_mW=4, _1000_mW=5, _2000_mW=6),
    "downlink_rssi" / Int8ub,
    "downlink_link_quality" / Int8ub,
    "downlink_snr" / Int8sb,
    "antenna_selection" / FlagsEnum(Int8ub, DIVERSITY=0x01, ANTENNA_1=0x02, ANTENNA_2=0x04),
)

# RC channels packed packet structure
payload_rc_channels_packed = ByteSwapped(
    BitStruct("channels" / Array(16, BitsInteger(11)))
)

# Subset RC channels packed packet structure
payload_subset_rc_channels_packed = ByteSwapped(
    BitStruct("channels" / Array(8, BitsInteger(11)))
)

# Attitude packet structure
payload_attitude = Struct(
    "pitch" / Int16sb,  # degrees * 100
    "roll" / Int16sb,   # degrees * 100
    "yaw" / Int16sb,    # degrees * 100
)

# Flight mode packet structure
payload_flight_mode = Struct(
    "origin_device_address" / Int8ub,
    "flight_mode" / GreedyBytes,  # Null-terminated string
)

# Ping devices packet structure
payload_ping_devices = Struct(
    "origin_device_address" / Int8ub,
    "destination_address" / Int8ub,
)

# Device info packet structure
payload_device_info = Struct(
    "origin_device_address" / Int8ub,
    "destination_address" / Int8ub,
    "hardware_version" / Int8ub,
    "software_version" / Int8ub,
    "field_version" / Int8ub,
    "parameter_version" / Int8ub,
    "device_name" / Array(6, Int8ub),  # Null-terminated string
)

# Radio ID packet structure
payload_radio_id = Struct(
    "origin_address" / Int8ub,
    "destination_address" / Int8ub,
    "radio_id" / Int32ub,
)

# Parameter settings entry packet structure
payload_parameter_settings_entry = Struct(
    "parameter_index" / Int8ub,
    "parameter_type" / Enum(Int8ub, UINT8=0, INT8=1, UINT16=2, INT16=3, STRING=4),
    "parameter_value" / GreedyBytes,  # Variable length based on type
)

# Command packet structure
payload_command = Struct(
    "origin_address" / Int8ub,
    "destination_address" / Int8ub,
    "command_id" / Int8ub,
    "command_data" / GreedyBytes,  # Variable length command data
)