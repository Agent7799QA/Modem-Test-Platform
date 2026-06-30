from modem_test_platform.protocols.crossfire.commands import Commands
from modem_test_platform.protocols.crossfire.parsers.print_parser import PrintParser
from modem_test_platform.protocols.crossfire.parsers.stat_parser import StatParser


class CrossfireAdapter:

    def __init__(self, protocol):
        self.protocol = protocol

        self.print_parser = PrintParser()
        self.stat_parser = StatParser()

    def connect(self):
        self.protocol.transport.open()

    def disconnect(self):
        self.protocol.transport.close()

    def read_configuration(self):

        response = self.protocol.send_command(Commands.PRINT)

        return self.print_parser.parse(response)

    def read_link_state(self):

        response = self.protocol.send_command(Commands.STAT)

        return self.stat_parser.parse(response)