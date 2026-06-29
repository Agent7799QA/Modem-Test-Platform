from modem_test_platform.transport.serial.serial_transport import SerialTransport
from modem_test_platform.protocols.crossfire.crossfire_protocol import CrossfireProtocol
from modem_test_platform.devices.adapters.crossfire.crossfire_adapter import CrossfireAdapter


def main():

    transport = SerialTransport("COM5")      # потом вынесем

    protocol = CrossfireProtocol(transport)

    modem = CrossfireAdapter(protocol)

    modem.connect()

    ok, response = modem.send("help")

    print(ok)
    print(response)

    modem.disconnect()


if __name__ == "__main__":
    main()