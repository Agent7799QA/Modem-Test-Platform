import time
from typing import Optional

from modem_test_platform.devices.configuration import Configuration
from modem_test_platform.protocols.crossfire.commands import Commands
from modem_test_platform.protocols.crossfire.parsers.print_parser import PrintParser
from modem_test_platform.protocols.crossfire.parsers.stat_parser import StatParser
from modem_test_platform.protocols.crossfire.parsers.ttlstat_parser import TtlStatParser


class CrossfireAdapter:

    def __init__(self, protocol):
        self.protocol = protocol
        self.print_parser = PrintParser()
        self.stat_parser = StatParser()
        self.ttlstat_parser = TtlStatParser()

    def connect(self):
        self.protocol.transport.open()

    def disconnect(self):
        self.protocol.transport.close()

    def read_configuration(self) -> Configuration:
        """Прочитать конфигурацию модема (команда print)."""
        response = self.protocol.send_command(Commands.PRINT)
        return self.print_parser.parse(response)

    def read_link_state(self):
        """Прочитать состояние линка (команда stat)."""
        response = self.protocol.send_command(Commands.STAT)
        return self.stat_parser.parse(response)

    def read_ttl_stats(self):
        """Прочитать TTL статистику (команда ttlstat)."""
        response = self.protocol.send_command(Commands.TTLSTAT)
        return self.ttlstat_parser.parse(response)

    def _send_command_and_verify(self, command: str, expected_value, verify_func) -> bool:
        """
        Отправить команду и проверить изменение через print.

        Raises:
            ValueError: Если модем вернул ошибку (Not supported value)
        """
        # 1. Отправить команду
        response = self.protocol.send_command(command)

        # 2. Проверить ответ на ошибку
        if "Not supported" in response or "Error" in response:
            error_msg = response.strip()
            raise ValueError(f"Модем вернул ошибку: {error_msg}")

        # 3. Задержка для применения
        time.sleep(0.2)

        # 4. Прочитать конфигурацию
        config = self.read_configuration()

        # 5. Проверить изменение
        actual_value = verify_func(config)
        return actual_value == expected_value

    # ========== Управление радио ==========

    def set_frequency(self, freq: int) -> bool:
        """Установить частоту (3500, 4000, 4500, 6500 MHz)."""
        if freq not in [3500, 4000, 4500, 6500]:
            raise ValueError(f"Not supported value: {freq}. Supported: 3500, 4000, 4500, 6500")

        return self._send_command_and_verify(
            f"freq {freq}",
            freq,
            lambda cfg: cfg.frequency
        )

    def set_fhss_mode(self, mode: int) -> bool:
        """Установить режим FHSS (0-4)."""
        if mode not in range(0, 5):
            raise ValueError(f"Not supported value: {mode}. Supported: 0, 1, 2, 3, 4")

        return self._send_command_and_verify(
            f"fhss {mode}",
            mode,
            lambda cfg: cfg.fhss
        )

    def set_dsss_mode(self, mode: int) -> bool:
        """Установить режим DSSS (0-7, рабочие 0-3)."""
        if mode not in range(0, 8):
            raise ValueError(f"Not supported value: {mode}. Supported: 0-7")

        return self._send_command_and_verify(
            f"dsss {mode}",
            mode,
            lambda cfg: cfg.dsss
        )

    def set_mode(self, mode: str) -> bool:
        """Установить режим работы (swarm+, swarm, longrange)."""
        if mode not in ["swarm+", "swarm", "longrange"]:
            raise ValueError(f"Not supported value: {mode}. Supported: 'swarm+', 'swarm', 'longrange'")

        return self._send_command_and_verify(
            f"mode {mode}",
            mode,
            lambda cfg: cfg.mode
        )

    def set_channel_code(self, code: int) -> bool:
        """Установить код канала (1-24)."""
        if code not in range(1, 25):
            raise ValueError(f"Not supported value: {code}. Supported: 1-24")

        return self._send_command_and_verify(
            f"code {code}",
            code,
            lambda cfg: cfg.channel_code
        )

    def set_attenuation(self, value: int) -> bool:
        """Установить аттенюацию (0-30 dB)."""
        if value not in range(0, 31):
            raise ValueError(f"Not supported value: {value}. Supported: 0-30")

        return self._send_command_and_verify(
            f"attenuation {value}",
            value,
            lambda cfg: cfg.attenuation
        )

    def set_rate(self, rate: int) -> bool:
        """Установить частоту отправки (5, 10, 25, 40, 50 Hz)."""
        if rate not in [5, 10, 25, 40, 50]:
            raise ValueError(f"Not supported value: {rate}. Supported: 5, 10, 25, 40, 50")

        return self._send_command_and_verify(
            f"rate {rate}",
            rate,
            lambda cfg: cfg.link_rate
        )

    # ========== Сетевые настройки ==========

    def set_pan(self, pan: int) -> bool:
        """Установить адрес сети (0-65534)."""
        if pan not in range(0, 65535):
            raise ValueError(f"Not supported value: {pan}. Supported: 0-65534")

        return self._send_command_and_verify(
            f"pan {pan}",
            pan,
            lambda cfg: cfg.network_address
        )

    def set_bind_address(self, address: int) -> bool:
        """Установить адрес управления (0-65534)."""
        if address not in range(0, 65535):
            raise ValueError(f"Not supported value: {address}. Supported: 0-65534")

        return self._send_command_and_verify(
            f"bind {address}",
            address,
            lambda cfg: cfg.bind_address
        )

    # ========== Управление ==========

    def set_protocol(self, protocol: str) -> bool:
        """Установить протокол (crsf_parser, sbus, mavlink, raw)."""
        if protocol not in ["crsf_parser", "sbus", "mavlink", "raw"]:
            raise ValueError(f"Not supported value: {protocol}. Supported: 'crsf_parser', 'sbus', 'mavlink', 'raw'")

        return self._send_command_and_verify(
            f"protocol {protocol}",
            protocol,
            lambda cfg: cfg.protocol
        )

    def set_timeslot(self, slot: int) -> bool:
        """Установить режим временного деления (0, 1, 2)."""
        if slot not in [0, 1, 2]:
            raise ValueError(f"Not supported value: {slot}. Supported: 0, 1, 2")

        return self._send_command_and_verify(
            f"timeslot {slot}",
            bool(slot),
            lambda cfg: cfg.time_slotting
        )

    # ========== Toggle-команды ==========

    def _toggle_parameter(self, command: str, get_state_func, set_state_func) -> bool:
        """
        Общий метод для toggle-команд.

        Args:
            command: Команда для отправки
            get_state_func: Функция для получения текущего состояния из Configuration
            set_state_func: Функция для установки состояния в Configuration (не используется)

        Returns:
            True если состояние изменилось
        """
        # 1. Получить текущее состояние
        old_config = self.read_configuration()
        old_state = get_state_func(old_config)

        # 2. Отправить команду
        response = self.protocol.send_command(command)

        # 3. Проверить ответ на ошибку
        if "Not supported" in response or "Error" in response:
            raise ValueError(f"Модем вернул ошибку: {response.strip()}")

        time.sleep(0.2)

        # 4. Прочитать новое состояние
        new_config = self.read_configuration()
        new_state = get_state_func(new_config)

        # 5. Проверить изменение
        return new_state != old_state and new_state is not None

    def toggle_led(self) -> bool:
        """Переключить состояние светодиода (toggle)."""
        return self._toggle_parameter(
            "led",
            lambda cfg: cfg.led_state,
            lambda cfg, val: setattr(cfg, 'led_state', val)
        )

    def toggle_ew_tests(self) -> bool:
        """Переключить режим РЭБ тестов (toggle)."""
        return self._toggle_parameter(
            "ewtests",
            lambda cfg: cfg.ew_tests,
            lambda cfg, val: setattr(cfg, 'ew_tests', val)
        )

    def toggle_retransmissions(self) -> bool:
        """Переключить ретрансляции (TTL) - только для TX."""
        return self._toggle_parameter(
            "ttl",
            lambda cfg: cfg.retransmissions,
            lambda cfg, val: setattr(cfg, 'retransmissions', val)
        )

    def toggle_acknowledge(self) -> bool:
        """Переключить подтверждения (ack) - только для TX."""
        return self._toggle_parameter(
            "ack",
            lambda cfg: cfg.acknowledge,
            lambda cfg, val: setattr(cfg, 'acknowledge', val)
        )

    # ========== Специальные команды ==========

    def reboot(self) -> bool:
        """Перезагрузить модем."""
        response = self.protocol.send_command("reboot")

        if "ESP-ROM" not in response:
            return False

        time.sleep(1.0)
        return self.protocol._check_connection()

    def get_help(self) -> str:
        """Получить справку по командам (сырой ответ)."""
        return self.protocol.send_command("help")