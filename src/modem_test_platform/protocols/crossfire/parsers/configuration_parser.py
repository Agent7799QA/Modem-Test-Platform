import re

from modem_test_platform.devices.configuration import Configuration


class ConfigurationParser:
    """Парсер ответа команды 'print'."""

    _INT = re.compile(r"-?\d+")

    @staticmethod
    def _number(text: str) -> int | None:
        match = ConfigurationParser._INT.search(text)
        return int(match.group()) if match else None

    def parse(self, response: str) -> Configuration:

        cfg = Configuration(raw=response)

        for raw_line in response.splitlines():

            line = raw_line.strip()

            if not line:
                continue

            # ---------- Device ----------

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

            # ---------- Protocol ----------

            elif line.startswith("RC protocol:"):
                cfg.protocol = line.split(":", 1)[1].strip()

            elif line.startswith("Preset:"):
                cfg.preset = (
                    line.split(":", 1)[1]
                    .replace(".", "")
                    .strip()
                )

            # ---------- Radio ----------

            elif "Mode:" in line:
                value = line.split("Mode:", 1)[1]
                cfg.mode = value.replace(".", "").strip()

            elif "Link rate:" in line:
                cfg.link_rate = self._number(line)

            elif "Central frequency:" in line:
                cfg.frequency = self._number(line)

            elif "Channel code:" in line:
                cfg.channel_code = self._number(line)

            elif "Attenuation:" in line:
                cfg.attenuation = self._number(line)

            elif "Module address:" in line:
                cfg.module_address = self._number(line)

            elif "Network address:" in line:
                cfg.network_address = self._number(line)

            elif "Binded address:" in line:
                cfg.bind_address = self._number(line)

            elif "Crystal trim:" in line:
                cfg.crystal_trim = self._number(line)

            elif "FHSS mode:" in line:
                cfg.fhss = self._number(line)

            elif "DSSS mode:" in line:
                cfg.dsss = self._number(line)

            # ---------- TX ----------

            elif "Time slotting:" in line:
                cfg.time_slotting = "enabled" in line.lower()

            elif "Retransmissions:" in line:
                cfg.retransmissions = "enable" in line.lower()

            elif "Acknowledge:" in line:
                cfg.acknowledge = "enable" in line.lower()

            elif "Max clients:" in line:
                cfg.max_clients = self._number(line)

            # ---------- RX ----------

            elif "EW tests:" in line:
                cfg.ew_tests = "enabled" in line.lower()

            # ---------- Serial ----------

            elif "Baudrate:" in line:
                cfg.baudrate = self._number(line)

            elif "Parity:" in line:
                text = line.split("Parity:", 1)[1]

                if "none" in text.lower():
                    cfg.parity = "none"
                elif "even" in text.lower():
                    cfg.parity = "even"
                elif "odd" in text.lower():
                    cfg.parity = "odd"

                stop = re.search(r"Stop bits:\s*(\d+)", text)

                if stop:
                    cfg.stop_bits = int(stop.group(1))

        return cfg