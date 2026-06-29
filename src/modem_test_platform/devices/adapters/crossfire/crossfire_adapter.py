from modem_test_platform.protocols.crossfire.crossfire_protocol import CrossfireProtocol
from modem_test_platform.protocols.crossfire.parser import CrossfireParser


class CrossfireAdapter:

    def __init__(self, protocol: CrossfireProtocol):
        self.protocol = protocol

    def connect(self):
        self.protocol.transport.open()

    def disconnect(self):
        self.protocol.transport.close()

    def send(self, command: str):

        response = self.protocol.send_command(command)

        return (
            CrossfireParser.is_success(response),
            response,
        )