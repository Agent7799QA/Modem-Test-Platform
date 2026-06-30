import re

from modem_test_platform.devices.configuration import Configuration


class PrintParser:
    """Парсер ответа команды 'print'."""

    _INT = re.compile(r"-?\d+")

    @staticmethod
    def _number(text: str) -> int | None:
        match = PrintParser._INT.search(text)
        return int(match.group()) if match else None

    @staticmethod
    def _get_int(text: str, marker: str) -> int | None:
        start = text.find(marker)
        if start == -1:
            return None
        return PrintParser._number(text[start:])

    @staticmethod
    def _get_string(text: str, marker: str) -> str | None:
        start = text.find(marker)
        if start == -1:
            return None
        value = text[start + len(marker):].strip()
        return value.replace(".", "").strip() if value else None

    @staticmethod
    def _get_bool(text: str, marker: str) -> bool | None:
        start = text.find(marker)
        if start == -1:
            return None
        value = text[start + len(marker):].strip().lower()
        return "enable" in value or "on" in value

    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """Извлечь секцию между маркерами."""
        start = text.find(start_marker)
        if start == -1:
            return ""

        end = text.find(end_marker, start)
        if end == -1:
            return text[start:]

        return text[start:end]

    def _parse_device_section(self, cfg: Configuration, section: str) -> None:
        """Парсинг секции Device."""
        for line in section.splitlines():
            line = line.strip()
            if not line:
                continue

            if "Drone RC (RX)" in line:
                cfg.device_type = "RX"
            elif "Drone RC (TX)" in line:
                cfg.device_type = "TX"
            elif line.startswith("Version:"):
                cfg.version = line.split(":", 1)[1].strip()
            elif line.startswith("SN:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    cfg.serial_number = value

    def _parse_radio_section(self, cfg: Configuration, section: str) -> None:
        """Парсинг секции Radio."""
        cfg.mode = self._get_string(section, "Mode:")
        cfg.link_rate = self._get_int(section, "Link rate:")
        cfg.frequency = self._get_int(section, "Central frequency:")
        cfg.channel_code = self._get_int(section, "Channel code:")
        cfg.attenuation = self._get_int(section, "Attenuation:")
        cfg.module_address = self._get_int(section, "Module address:")
        cfg.network_address = self._get_int(section, "Network address:")
        cfg.bind_address = self._get_int(section, "Binded address:")
        cfg.crystal_trim = self._get_int(section, "Crystal trim:")
        cfg.fhss = self._get_int(section, "FHSS mode:")
        cfg.dsss = self._get_int(section, "DSSS mode:")
        cfg.time_slotting = self._get_bool(section, "Time slotting:")
        cfg.retransmissions = self._get_bool(section, "Retransmissions:")
        cfg.acknowledge = self._get_bool(section, "Acknowledge:")
        cfg.max_clients = self._get_int(section, "Max clients:")
        cfg.ew_tests = self._get_bool(section, "EW tests:")

    def _parse_serial_section(self, cfg: Configuration, section: str) -> None:
        """Парсинг секции Serial."""
        cfg.baudrate = self._get_int(section, "Baudrate:")

        if "Parity:" in section:
            text = section.split("Parity:", 1)[1]
            if "none" in text.lower():
                cfg.parity = "none"
            elif "even" in text.lower():
                cfg.parity = "even"
            elif "odd" in text.lower():
                cfg.parity = "odd"

        cfg.stop_bits = self._get_int(section, "Stop bits:")

        if "Not inverted" in section:
            cfg.inverted = False
        elif "Inverted" in section:
            cfg.inverted = True

    def _parse_protocol_section(self, cfg: Configuration, section: str) -> None:
        """Парсинг секции Protocol."""
        for line in section.splitlines():
            line = line.strip()
            if not line:
                continue

            if line.startswith("RC protocol:"):
                cfg.protocol = line.split(":", 1)[1].strip()
            elif line.startswith("Preset:"):
                cfg.preset = line.split(":", 1)[1].replace(".", "").strip()

    def _parse_external_section(self, cfg: Configuration, section: str) -> None:
        """Парсинг секции External Interface."""
        # Можно добавить парсинг pin'ов, если нужно
        pass

    def parse(self, response: str) -> Configuration:
        cfg = Configuration(raw=response)

        # Извлекаем секции
        device_section = self._extract_section(response, "", "Radio:")
        radio_section = self._extract_section(response, "Radio:", "Serial:")
        serial_section = self._extract_section(response, "Serial:", "External interface:")
        protocol_section = self._extract_section(response, "RC protocol:", "\n")  # до конца или до Radio

        # Парсим каждую секцию
        self._parse_device_section(cfg, device_section)
        self._parse_radio_section(cfg, radio_section)
        self._parse_serial_section(cfg, serial_section)
        self._parse_protocol_section(cfg, protocol_section)
        self._parse_external_section(cfg, response)

        return cfg