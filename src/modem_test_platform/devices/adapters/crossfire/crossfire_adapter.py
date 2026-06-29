from modem_test_platform.protocols.crossfire.parser import CrossfireParser
from modem_test_platform.protocols.crossfire.parsers.link_state_parser import LinkStateParser
from modem_test_platform.protocols.crossfire.commands import Commands

class CrossfireAdapter:

    def __init__(self, protocol):
        self.protocol = protocol
        self.parser = LinkStateParser()

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

    def read_link_state(self):
        response = self.protocol.send_command(Commands.STAT)

        return self.parser.parse(response)