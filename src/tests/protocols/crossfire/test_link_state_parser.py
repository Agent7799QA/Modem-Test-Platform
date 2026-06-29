from modem_test_platform.protocols.crossfire.parsers.link_state_parser import (
    LinkStateParser,
)


def test_parse_stat():

    response = (
        "> Uplink LQ: 97, "
        "Uplink RSSI: -63 dBm, "
        "Downlink LQ: 99, "
        "Downlink RSSI: -61 dBm"
    )

    parser = LinkStateParser()

    state = parser.parse(response)

    assert state.uplink_lq == 97
    assert state.uplink_rssi == -63
    assert state.downlink_lq == 99
    assert state.downlink_rssi == -61