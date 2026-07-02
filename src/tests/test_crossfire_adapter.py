"""
Тесты для CrossfireAdapter с использованием pytest
"""

import pytest
from unittest.mock import Mock, patch
from modem_test_platform.devices import CrossfireAdapter
from modem_test_platform.devices import Configuration


@pytest.fixture
def mock_protocol():
    """Фикстура для мока протокола."""
    return Mock()


@pytest.fixture
def adapter(mock_protocol):
    """Фикстура для адаптера."""
    return CrossfireAdapter(mock_protocol)


def test_connect(adapter, mock_protocol):
    """Тест подключения."""
    adapter.connect()
    mock_protocol.transport.open.assert_called_once()


def test_disconnect(adapter, mock_protocol):
    """Тест отключения."""
    adapter.disconnect()
    mock_protocol.transport.close.assert_called_once()


def test_read_configuration(adapter, mock_protocol):
    """Тест чтения конфигурации."""
    mock_response = """Drone RC (RX)
Version: 4.0.10
SN: 736ae9eafcdfeb4d
Onboard LED is OFF
RC protocol: crsf_parser
Radio:
    Mode:           Long range
    Link rate:      50
    Central frequency:  3500 MHz
    Channel code:       11
    Attenuation:        30 dB
    Module address:     29131
    Network address:    56064
    Binded address:     1111
    Crystal trim:       111
    FHSS mode:          0
    DSSS mode:          0
    EW tests:           enabled
Serial:
    Baudrate:       420000
    Parity:         none
    Stop bits:      1
    Not inverted
External interface:
    Interface mode:     off
External pins:
    Pin 0:
        Mode:   debug
        Dependency: 13
    Pin 1:
        Mode:   off
        Dependency: 14"""

    mock_protocol.send_command.return_value = mock_response

    config = adapter.read_configuration()

    mock_protocol.send_command.assert_called_once()
    assert config.device_type == "RX"
    assert config.version == "4.0.10"
    assert config.serial_number == "736ae9eafcdfeb4d"
    assert config.led_state is False
    assert config.frequency == 3500
    assert config.fhss == 0
    assert config.dsss == 0


@pytest.mark.parametrize("freq, expected_success", [
    (3500, True),
    (4000, True),
    (4500, True),
    (6500, True),
    (3000, False),
    (2500, False),
    (5000, False),
])
def test_set_frequency(adapter, mock_protocol, freq, expected_success):
    """Тест установки частоты с параметризацией."""
    if expected_success:
        mock_protocol.send_command.return_value = ""
    else:
        mock_protocol.send_command.return_value = f"Not supported value: {freq}"

    with patch.object(adapter, 'read_configuration') as mock_read:
        if expected_success:
            mock_config = Configuration(frequency=freq)
            mock_read.return_value = mock_config
            result = adapter.set_frequency(freq)
            assert result is True
        else:
            with pytest.raises(ValueError) as exc_info:
                adapter.set_frequency(freq)
            assert "Not supported" in str(exc_info.value)


@pytest.mark.parametrize("mode, expected_success", [
    ("swarm+", True),
    ("swarm", True),
    ("longrange", True),
    ("swarm-", False),
    ("invalid", False),
])
def test_set_mode(adapter, mock_protocol, mode, expected_success):
    """Тест установки режима с параметризацией."""
    if expected_success:
        mock_protocol.send_command.return_value = ""
    else:
        mock_protocol.send_command.return_value = f"Not supported value: {mode}"

    with patch.object(adapter, 'read_configuration') as mock_read:
        if expected_success:
            mock_config = Configuration(mode=mode)
            mock_read.return_value = mock_config
            result = adapter.set_mode(mode)
            assert result is True
        else:
            with pytest.raises(ValueError) as exc_info:
                adapter.set_mode(mode)
            assert "Not supported" in str(exc_info.value)


@pytest.mark.parametrize("fhss_mode, expected_success", [
    (0, True),
    (1, True),
    (2, True),
    (3, True),
    (4, True),
    (5, False),
    (-1, False),
])
def test_set_fhss_mode(adapter, mock_protocol, fhss_mode, expected_success):
    """Тест установки FHSS режима."""
    if expected_success:
        mock_protocol.send_command.return_value = ""
    else:
        mock_protocol.send_command.return_value = f"Not supported value: {fhss_mode}"

    with patch.object(adapter, 'read_configuration') as mock_read:
        if expected_success:
            mock_config = Configuration(fhss=fhss_mode)
            mock_read.return_value = mock_config
            result = adapter.set_fhss_mode(fhss_mode)
            assert result is True
        else:
            with pytest.raises(ValueError):
                adapter.set_fhss_mode(fhss_mode)


@pytest.mark.parametrize("dsss_mode, expected_success", [
    (0, True),
    (1, True),
    (2, True),
    (3, True),
    (7, True),
    (8, False),
    (-1, False),
])
def test_set_dsss_mode(adapter, mock_protocol, dsss_mode, expected_success):
    """Тест установки DSSS режима."""
    if expected_success:
        mock_protocol.send_command.return_value = ""
    else:
        mock_protocol.send_command.return_value = f"Not supported value: {dsss_mode}"

    with patch.object(adapter, 'read_configuration') as mock_read:
        if expected_success:
            mock_config = Configuration(dsss=dsss_mode)
            mock_read.return_value = mock_config
            result = adapter.set_dsss_mode(dsss_mode)
            assert result is True
        else:
            with pytest.raises(ValueError):
                adapter.set_dsss_mode(dsss_mode)


@pytest.mark.parametrize("code, expected_success", [
    (1, True),
    (24, True),
    (0, False),
    (25, False),
])
def test_set_channel_code(adapter, mock_protocol, code, expected_success):
    """Тест установки кода канала."""
    if expected_success:
        mock_protocol.send_command.return_value = ""
    else:
        mock_protocol.send_command.return_value = f"Not supported value: {code}"

    with patch.object(adapter, 'read_configuration') as mock_read:
        if expected_success:
            mock_config = Configuration(channel_code=code)
            mock_read.return_value = mock_config
            result = adapter.set_channel_code(code)
            assert result is True
        else:
            with pytest.raises(ValueError):
                adapter.set_channel_code(code)


@pytest.mark.parametrize("value, expected_success", [
    (0, True),
    (30, True),
    (-1, False),
    (31, False),
])
def test_set_attenuation(adapter, mock_protocol, value, expected_success):
    """Тест установки аттенюации."""
    if expected_success:
        mock_protocol.send_command.return_value = ""
    else:
        mock_protocol.send_command.return_value = f"Not supported value: {value}"

    with patch.object(adapter, 'read_configuration') as mock_read:
        if expected_success:
            mock_config = Configuration(attenuation=value)
            mock_read.return_value = mock_config
            result = adapter.set_attenuation(value)
            assert result is True
        else:
            with pytest.raises(ValueError):
                adapter.set_attenuation(value)


@pytest.mark.parametrize("rate, expected_success", [
    (5, True),
    (10, True),
    (25, True),
    (40, True),
    (50, True),
    (30, False),
    (100, False),
])
def test_set_rate(adapter, mock_protocol, rate, expected_success):
    """Тест установки частоты отправки."""
    if expected_success:
        mock_protocol.send_command.return_value = ""
    else:
        mock_protocol.send_command.return_value = f"Not supported value: {rate}"

    with patch.object(adapter, 'read_configuration') as mock_read:
        if expected_success:
            mock_config = Configuration(link_rate=rate)
            mock_read.return_value = mock_config
            result = adapter.set_rate(rate)
            assert result is True
        else:
            with pytest.raises(ValueError):
                adapter.set_rate(rate)


@pytest.mark.parametrize("protocol, expected_success", [
    ("crsf_parser", True),
    ("sbus", True),
    ("mavlink", True),
    ("raw", True),
    ("invalid", False),
])
def test_set_protocol(adapter, mock_protocol, protocol, expected_success):
    """Тест установки протокола."""
    if expected_success:
        mock_protocol.send_command.return_value = ""
    else:
        mock_protocol.send_command.return_value = f"Not supported value: {protocol}"

    with patch.object(adapter, 'read_configuration') as mock_read:
        if expected_success:
            mock_config = Configuration(protocol=protocol)
            mock_read.return_value = mock_config
            result = adapter.set_protocol(protocol)
            assert result is True
        else:
            with pytest.raises(ValueError):
                adapter.set_protocol(protocol)


def test_read_link_state(adapter, mock_protocol):
    """Тест чтения состояния канала."""
    mock_response = "Uplink LQ: 95, Uplink RSSI: 65 dBm, Downlink LQ: 90, Downlink RSSI: 70 dBm"
    mock_protocol.send_command.return_value = mock_response

    state = adapter.read_link_state()

    mock_protocol.send_command.assert_called_once()
    assert state.uplink_lq == 95
    assert state.uplink_rssi == 65
    assert state.downlink_lq == 90
    assert state.downlink_rssi == 70


def test_toggle_led(adapter, mock_protocol):
    """Тест переключения LED."""
    mock_protocol.send_command.return_value = ""

    with patch.object(adapter, 'read_configuration') as mock_read:
        mock_read.side_effect = [
            Configuration(led_state=False),
            Configuration(led_state=True),
        ]

        result = adapter.toggle_led()
        assert result is True
        assert mock_protocol.send_command.call_count == 1
        assert mock_read.call_count == 2


def test_toggle_led_no_change(adapter, mock_protocol):
    """Тест переключения LED - состояние не изменилось."""
    mock_protocol.send_command.return_value = ""

    with patch.object(adapter, 'read_configuration') as mock_read:
        mock_read.side_effect = [
            Configuration(led_state=False),
            Configuration(led_state=False),
        ]

        result = adapter.toggle_led()
        assert result is False
        assert mock_protocol.send_command.call_count == 1
        assert mock_read.call_count == 2


def test_toggle_led_error(adapter, mock_protocol):
    """Тест переключения LED - ошибка от модема."""
    mock_protocol.send_command.return_value = "Not supported value: led"

    with pytest.raises(ValueError) as exc_info:
        adapter.toggle_led()

    assert "Not supported" in str(exc_info.value)


def test_reboot(adapter, mock_protocol):
    """Тест перезагрузки."""
    mock_protocol.send_command.return_value = "ESP-ROM:esp32s3-20210327"

    with patch.object(adapter.protocol, '_check_connection', return_value=True):
        result = adapter.reboot()
        assert result is True
        mock_protocol.send_command.assert_called_with("reboot")


def test_reboot_failure(adapter, mock_protocol):
    """Тест перезагрузки - неудача."""
    mock_protocol.send_command.return_value = "reboot"

    result = adapter.reboot()
    assert result is False


def test_read_ttl_stats(adapter, mock_protocol):
    """Тест чтения TTL статистики."""
    mock_response = """Recieved statistic for last 10 seconds:
ttl 7: 0
ttl 6: 0
ttl 5: 0
ttl 4: 0
ttl 3: 0
ttl 2: 0
ttl 1: 0
ttl 0: 0"""

    mock_protocol.send_command.return_value = mock_response

    stats = adapter.read_ttl_stats()

    mock_protocol.send_command.assert_called_once()
    assert stats.ttl_0 == 0
    assert stats.ttl_1 == 0
    assert stats.ttl_2 == 0
    assert stats.ttl_3 == 0
    assert stats.ttl_4 == 0
    assert stats.ttl_5 == 0
    assert stats.ttl_6 == 0
    assert stats.ttl_7 == 0
    assert stats.time_window == "last 10 seconds"


def test_get_help(adapter, mock_protocol):
    """Тест получения справки."""
    mock_response = "Drone RC (RX)\nVersion: 4.0.10"
    mock_protocol.send_command.return_value = mock_response

    result = adapter.get_help()

    assert result == mock_response
    mock_protocol.send_command.assert_called_with("help")