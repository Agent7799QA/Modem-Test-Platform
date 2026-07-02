from construct import Byte, If, Struct, Const, Int8ub, Switch, Tell, this, Array, Select
from crossfire.crsf_parser.payloads import (
    PacketsTypes,
    payload_battery_sensor,
    payload_heartbeat,
    payload_link_statistics,
    payload_rc_channels_packed,
    payload_gps,
    payload_varios,
    payload_baro_altitude,
    payload_vtx,
    payload_vtx_text,
    payload_subset_rc_channels_packed,
    payload_link_statistics_extended,
    payload_attitude,
    payload_flight_mode,
    payload_ping_devices,
    payload_device_info,
    payload_parameter_settings_entry,
    payload_command,
    payload_radio_id,
    GreedyBytes
)

SYNC_RX_BYTE_BIN_STRING = b"\xc8"
SYNC_TX_BYTE_BIN_STRING = b"\xea"
SYNC_RADIO_BYTE_BIN_STRING = b"\xee"
SYNC_RX_BYTE = int.from_bytes(SYNC_RX_BYTE_BIN_STRING, byteorder="big")
SYNC_TX_BYTE = int.from_bytes(SYNC_TX_BYTE_BIN_STRING, byteorder="big")

crsf_header = Struct(
    "sync_byte" / Select(Const(SYNC_RX_BYTE_BIN_STRING), Const(SYNC_TX_BYTE_BIN_STRING)),
    "frame_length" / Int8ub,
    "data_offset" / Tell,
    "type" / Int8ub,
    "destination_address" / If(this.type > 0x27, Int8ub),
    "origin_address" / If(this.type > 0x27, Int8ub),
)

crsf_frame = Struct(
    "header" / crsf_header,
    "payload"
    / Switch(
        this.header.type,
        {
            PacketsTypes.GPS: payload_gps,
            PacketsTypes.VARIOS: payload_varios,
            PacketsTypes.BATTERY_SENSOR: payload_battery_sensor,
            PacketsTypes.BARO_ALTITUDE: payload_baro_altitude,
            PacketsTypes.HEARTBEAT: payload_heartbeat,
            PacketsTypes.VTX: payload_vtx,
            PacketsTypes.VTX_TEXT: payload_vtx_text,
            PacketsTypes.LINK_STATISTICS: payload_link_statistics,
            PacketsTypes.RC_CHANNELS_PACKED: payload_rc_channels_packed,
            PacketsTypes.SUBSET_RC_CHANNELS_PACKED: payload_subset_rc_channels_packed,
            PacketsTypes.LINK_STATISTICS_EXTENDED: payload_link_statistics_extended,
            PacketsTypes.ATTITUDE: payload_attitude,
            PacketsTypes.FLIGHT_MODE: payload_flight_mode,
            PacketsTypes.PING_DEVICES: payload_ping_devices,
            PacketsTypes.DEVICE_INFO: payload_device_info,
            PacketsTypes.REQUEST_SETTINGS: Struct("destination_address" / Int8ub),
            PacketsTypes.PARAMETER_SETTINGS_ENTRY: payload_parameter_settings_entry,
            PacketsTypes.PARAMETER_READ: Struct("parameter_index" / Int8ub),
            PacketsTypes.PARAMETER_WRITE: payload_parameter_settings_entry,
            PacketsTypes.COMMAND: payload_command,
            PacketsTypes.RADIO_ID: payload_radio_id,
            PacketsTypes.OSD: GreedyBytes,
            PacketsTypes.MSP_REQ: GreedyBytes,
            PacketsTypes.MSP_RESP: GreedyBytes,
            PacketsTypes.MSP_WRITE: GreedyBytes,
            PacketsTypes.ARDUPILOT_RESP: GreedyBytes,
        },
        default=Array(this.frame_length - 2, Byte),
    ),
    "crc_offset" / Tell,
    "CRC" / Int8ub,
)