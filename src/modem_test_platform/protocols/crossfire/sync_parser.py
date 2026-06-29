import re

from modem_test_platform.protocols.crossfire.models.sync_info import SyncInfo


class SyncParser:

    def parse(self, response: str) -> SyncInfo:

        info = SyncInfo(raw=response)

        return info