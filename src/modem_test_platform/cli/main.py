from modem_test_platform.transport.serial.serial_transport import SerialTransport
from modem_test_platform.protocols.crossfire.crossfire_protocol import CrossfireProtocol
from modem_test_platform.devices.adapters.crossfire.crossfire_adapter import CrossfireAdapter


def main():

    transport = SerialTransport("COM5")      # потом вынесем

    protocol = CrossfireProtocol(transport)

    modem = CrossfireAdapter(protocol)

    modem.connect()

    ok, response = modem.send("help")

    state = modem.read_link_state()

    print(ok)
    print(response)

    print(state)
    print(f"UL LQ   : {state.uplink_lq}")
    print(f"UL RSSI : {state.uplink_rssi}")
    print(f"DL LQ   : {state.downlink_lq}")
    print(f"DL RSSI : {state.downlink_rssi}")

    modem.disconnect()


if __name__ == "__main__":
    main()