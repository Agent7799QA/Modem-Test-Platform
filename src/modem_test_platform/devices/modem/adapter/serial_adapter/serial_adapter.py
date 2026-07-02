import logging
from typing import Callable

from modem_test_platform.devices.modem.modemconfiguration import ModemConfiguration
from modem_test_platform.protocols.crossfire.commands import Commands
from modem_test_platform.protocols.serial_protocol.parsers.print_parser import PrintParser
from modem_test_platform.protocols.serial_protocol.parsers.stat_parser import StatParser
from modem_test_platform.protocols.serial_protocol.parsers.ttlstat_parser import TtlStatParser


logger = logging.getLogger(__name__)


class SerialAdapter:
    def __init__(self, protocol):
        self.protocol = protocol
        self.print_parser = PrintParser()
        self.stat_parser = StatParser()
        self.ttlstat_parser = TtlStatParser()

    def connect(self):
        self.protocol.transport.open()

    def disconnect(self):
        self.protocol.transport.close()

    def is_connected(self) -> bool:
        return self.protocol.transport.is_open

    def read_configuration(self) -> ModemConfiguration:
        response = self.protocol.send_command(Commands.PRINT)
        return self.print_parser.parse(response)

    def read_link_state(self):
        response = self.protocol.send_command(Commands.STAT)
        return self.stat_parser.parse(response)

    def read_ttl_stats(self):
        response = self.protocol.send_command(Commands.TTLSTAT)
        return self.ttlstat_parser.parse(response)

    # ========== Базовые методы ==========

    def send_command(self, command: str, timeout: float = None) -> str:
        """Отправить команду."""
        return self.protocol.send_command(command, timeout=timeout)

    def check_error(self, response: str) -> None:
        """Проверить ответ на ошибку."""
        if "Not supported" in response or "Error" in response:
            raise ValueError(f"Модем вернул ошибку: {response.strip()}")

    def verify_change(
        self, expected_value, verify_func: Callable, max_retries: int = 3, delay: float = 0.15
    ) -> bool:
        """Проверить изменение параметра через print."""
        for attempt in range(max_retries):
            # time.sleep(delay)
            config = self.read_configuration()
            actual_value = verify_func(config)

            if isinstance(expected_value, str) and isinstance(actual_value, str):
                if actual_value.lower() == expected_value.lower():
                    logger.debug(f"Изменение подтверждено (попытка {attempt + 1})")
                    return True
            else:
                if actual_value == expected_value:
                    logger.debug(f"Изменение подтверждено (попытка {attempt + 1})")
                    return True

            logger.debug(
                f"Ожидается {expected_value}, получено {actual_value} (попытка {attempt + 1})"
            )

        logger.warning(f"Не удалось подтвердить изменение")
        return False

    # ========== Управление радио ==========

    def set_frequency(self, freq: int) -> bool:
        if freq not in [3500, 4000, 4500, 6500]:
            raise ValueError(f"Not supported value: {freq}. Supported: 3500, 4000, 4500, 6500")

        response = self.send_command(f"freq {freq}")
        self.check_error(response)
        return self.verify_change(freq, lambda cfg: cfg.frequency)

    def set_fhss_mode(self, mode: int) -> bool:
        if mode not in range(0, 5):
            raise ValueError(f"Not supported value: {mode}. Supported: 0, 1, 2, 3, 4")

        response = self.send_command(f"fhss {mode}")
        self.check_error(response)
        return self.verify_change(mode, lambda cfg: cfg.fhss)

    def set_dsss_mode(self, mode: int) -> bool:
        if mode not in range(0, 8):
            raise ValueError(f"Not supported value: {mode}. Supported: 0-7")

        response = self.send_command(f"dsss {mode}")
        self.check_error(response)
        return self.verify_change(mode, lambda cfg: cfg.dsss)

    def set_mode(self, mode: str) -> bool:
        if mode not in ["swarm+", "swarm", "longrange"]:
            raise ValueError(
                f"Not supported value: {mode}. Supported: 'swarm+', 'swarm', 'longrange'"
            )

        response = self.send_command(f"mode {mode}")
        self.check_error(response)
        return self.verify_change(
            mode.lower() if mode else None, lambda cfg: cfg.mode.lower() if cfg.mode else None
        )

    def set_channel_code(self, code: int) -> bool:
        if code not in range(1, 25):
            raise ValueError(f"Not supported value: {code}. Supported: 1-24")

        response = self.send_command(f"code {code}")
        self.check_error(response)
        return self.verify_change(code, lambda cfg: cfg.channel_code)

    def set_attenuation(self, value: int) -> bool:
        if value not in range(0, 31):
            raise ValueError(f"Not supported value: {value}. Supported: 0-30")

        response = self.send_command(f"attenuation {value}")
        self.check_error(response)
        return self.verify_change(value, lambda cfg: cfg.attenuation)

    def set_rate(self, rate: int) -> bool:
        if rate not in [5, 10, 25, 40, 50]:
            raise ValueError(f"Not supported value: {rate}. Supported: 5, 10, 25, 40, 50")

        response = self.send_command(f"rate {rate}")
        self.check_error(response)
        return self.verify_change(rate, lambda cfg: cfg.link_rate)

    def set_pan(self, pan: int) -> bool:
        if pan not in range(0, 65535):
            raise ValueError(f"Not supported value: {pan}. Supported: 0-65534")

        response = self.send_command(f"pan {pan}")
        self.check_error(response)
        return self.verify_change(pan, lambda cfg: cfg.network_address)

    def set_bind_address(self, address: int) -> bool:
        if address not in range(0, 65535):
            raise ValueError(f"Not supported value: {address}. Supported: 0-65534")

        response = self.send_command(f"bind {address}")
        self.check_error(response)
        return self.verify_change(address, lambda cfg: cfg.bind_address)

    def set_protocol(self, protocol: str) -> bool:
        if protocol not in ["crsf", "sbus", "mavlink", "raw"]:
            raise ValueError(
                f"Not supported value: {protocol}. Supported: 'crsf', 'sbus', 'mavlink', 'raw'"
            )

        response = self.send_command(f"protocol {protocol}")
        self.check_error(response)
        return self.verify_change(
            protocol.lower() if protocol else None,
            lambda cfg: cfg.protocol.lower() if cfg.protocol else None,
        )

    def set_timeslot(self, slot: int) -> bool:
        if slot not in [0, 1, 2]:
            raise ValueError(f"Not supported value: {slot}. Supported: 0, 1, 2")

        response = self.send_command(f"timeslot {slot}")
        self.check_error(response)
        return self.verify_change(bool(slot), lambda cfg: cfg.time_slotting)

    # ========== Toggle-команды ==========

    def _toggle_parameter(self, command: str, get_state_func) -> bool:
        old_config = self.read_configuration()
        old_state = get_state_func(old_config)

        response = self.send_command(command)
        self.check_error(response)

        for attempt in range(3):
            #time.sleep(0.15)
            new_config = self.read_configuration()
            new_state = get_state_func(new_config)

            if new_state != old_state and new_state is not None:
                logger.debug(f"Toggle '{command}' успешен (попытка {attempt + 1})")
                return True

        logger.warning(f"Не удалось подтвердить toggle после команды '{command}'")
        return False

    def toggle_led(self) -> bool:
        return self._toggle_parameter("led", lambda cfg: cfg.led_state)

    def toggle_ew_tests(self) -> bool:
        return self._toggle_parameter("ewtests", lambda cfg: cfg.ew_tests)

    def toggle_retransmissions(self) -> bool:
        return self._toggle_parameter("ttl", lambda cfg: cfg.retransmissions)

    def toggle_acknowledge(self) -> bool:
        return self._toggle_parameter("ack", lambda cfg: cfg.acknowledge)

    # ========== Специальные команды ==========

    def reboot(self) -> bool:
        try:
            response = self.send_command("reboot", timeout=3.0)
            self.check_error(response)

            if "ESP-ROM" not in response:
                logger.warning("Модем не начал перезагрузку (нет ESP-ROM)")
                return False

            if "Initialization done!" in response:
                logger.info("✅ Модем успешно перезагружен")
                return True

            logger.info("Ожидание завершения перезагрузки...")
            # time.sleep(2.0)

            return self.protocol.reopen()

        except Exception as e:
            logger.error(f"Ошибка при перезагрузке: {e}")
            return False

    def get_help(self) -> str:
        return self.send_command("help")
