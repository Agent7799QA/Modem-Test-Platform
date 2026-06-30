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
        self.ttlstat_parser = TtlStatParser()  # ✅ Добавлен

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

    # ========== Методы управления ==========

    def _send_command_and_verify(self, command: str, param_name: str, expected_value, verify_func) -> bool:
        """
        Отправить команду и проверить изменение через print.

        Args:
            command: Команда для отправки (например, "freq 4500")
            param_name: Имя параметра в Configuration
            expected_value: Ожидаемое значение
            verify_func: Функция для получения значения из Configuration

        Returns:
            True если параметр изменился, иначе False
        """
        # 1. Отправить команду1
        self.protocol.send_command(command)

        # 2. Небольшая задержка для применения
        time.sleep(0.1)

        # 3. Прочитать конфигурацию
        config = self.read_configuration()

        # 4. Проверить изменение
        actual_value = verify_func(config)
        return actual_value == expected_value

    def set_frequency(self, freq: int) -> bool:
        """Установить частоту (3500, 4000, 4500, 6500 MHz)."""
        return self._send_command_and_verify(
            f"freq {freq}",
            "frequency",
            freq,
            lambda cfg: cfg.frequency
        )

    def set_fhss_mode(self, mode: int) -> bool:
        """Установить режим FHSS (0-4)."""
        if mode not in range(0, 5):
            raise ValueError(f"FHSS mode must be 0-4, got {mode}")
        return self._send_command_and_verify(
            f"fhss {mode}",
            "fhss",
            mode,
            lambda cfg: cfg.fhss
        )

    def set_dsss_mode(self, mode: int) -> bool:
        """Установить режим DSSS (0-7, рабочие 0-3)."""
        if mode not in range(0, 8):
            raise ValueError(f"DSSS mode must be 0-7, got {mode}")
        return self._send_command_and_verify(
            f"dsss {mode}",
            "dsss",
            mode,
            lambda cfg: cfg.dsss
        )

    def set_mode(self, mode: str) -> bool:
        """Установить режим работы (swarm+, swarm, longrange)."""
        if mode not in ["swarm+", "swarm", "longrange"]:
            raise ValueError(f"Mode must be 'swarm+', 'swarm' or 'longrange', got {mode}")
        return self._send_command_and_verify(
            f"mode {mode}",
            "mode",
            mode,
            lambda cfg: cfg.mode
        )

    def set_channel_code(self, code: int) -> bool:
        """Установить код канала (1-24)."""
        if code not in range(1, 25):
            raise ValueError(f"Channel code must be 1-24, got {code}")
        return self._send_command_and_verify(
            f"code {code}",
            "channel_code",
            code,
            lambda cfg: cfg.channel_code
        )

    def set_attenuation(self, value: int) -> bool:
        """Установить аттенюацию (0-30 dB)."""
        if value not in range(0, 31):
            raise ValueError(f"Attenuation must be 0-30, got {value}")
        return self._send_command_and_verify(
            f"attenuation {value}",
            "attenuation",
            value,
            lambda cfg: cfg.attenuation
        )

    def set_rate(self, rate: int) -> bool:
        """Установить частоту отправки (5, 10, 25, 40, 50 Hz)."""
        if rate not in [5, 10, 25, 40, 50]:
            raise ValueError(f"Rate must be 5, 10, 25, 40 or 50, got {rate}")
        return self._send_command_and_verify(
            f"rate {rate}",
            "link_rate",
            rate,
            lambda cfg: cfg.link_rate
        )

    def set_pan(self, pan: int) -> bool:
        """Установить адрес сети (0-65534)."""
        if pan not in range(0, 65535):
            raise ValueError(f"PAN must be 0-65534, got {pan}")
        return self._send_command_and_verify(
            f"pan {pan}",
            "network_address",
            pan,
            lambda cfg: cfg.network_address
        )

    def set_bind_address(self, address: int) -> bool:
        """Установить адрес управления (0-65534)."""
        if address not in range(0, 65535):
            raise ValueError(f"Bind address must be 0-65534, got {address}")
        return self._send_command_and_verify(
            f"bind {address}",
            "bind_address",
            address,
            lambda cfg: cfg.bind_address
        )

    def set_protocol(self, protocol: str) -> bool:
        """Установить протокол (crsf, sbus, mavlink, raw)."""
        if protocol not in ["crsf", "sbus", "mavlink", "raw"]:
            raise ValueError(f"Protocol must be 'crsf', 'sbus', 'mavlink' or 'raw', got {protocol}")
        return self._send_command_and_verify(
            f"protocol {protocol}",
            "protocol",
            protocol,
            lambda cfg: cfg.protocol
        )

    def set_timeslot(self, slot: int) -> bool:
        """Установить режим временного деления (0, 1, 2)."""
        if slot not in [0, 1, 2]:
            raise ValueError(f"Timeslot must be 0, 1 or 2, got {slot}")
        return self._send_command_and_verify(
            f"timeslot {slot}",
            "time_slotting",
            bool(slot),
            lambda cfg: cfg.time_slotting
        )

    def toggle_led(self) -> bool:
        """
        Переключить состояние светодиода (toggle).
        Возвращает True если состояние изменилось.
        """
        # 1. Получить текущее состояние
        old_config = self.read_configuration()
        old_state = old_config.led_state

        # 2. Отправить команду
        self.protocol.send_command("led")
        time.sleep(0.1)

        # 3. Прочитать новое состояние
        new_config = self.read_configuration()
        new_state = new_config.led_state

        # 4. Проверить изменение
        return new_state != old_state and new_state is not None

    def toggle_ew_tests(self) -> bool:
        """
        Переключить режим РЭБ тестов (toggle).
        Возвращает True если состояние изменилось.
        """
        # 1. Получить текущее состояние
        old_config = self.read_configuration()
        old_state = old_config.ew_tests

        # 2. Отправить команду
        self.protocol.send_command("ewtests")
        time.sleep(0.1)

        # 3. Прочитать новое состояние
        new_config = self.read_configuration()
        new_state = new_config.ew_tests

        # 4. Проверить изменение
        return new_state != old_state and new_state is not None

    def toggle_retransmissions(self) -> bool:
        """
        Переключить ретрансляции (TTL) - только для TX.
        Возвращает True если состояние изменилось.
        """
        # 1. Получить текущее состояние
        old_config = self.read_configuration()
        old_state = old_config.retransmissions

        # 2. Отправить команду
        self.protocol.send_command("ttl")
        time.sleep(0.1)

        # 3. Прочитать новое состояние
        new_config = self.read_configuration()
        new_state = new_config.retransmissions

        # 4. Проверить изменение
        return new_state != old_state and new_state is not None

    def toggle_acknowledge(self) -> bool:
        """
        Переключить подтверждения (ack) - только для TX.
        Возвращает True если состояние изменилось.
        """
        # 1. Получить текущее состояние
        old_config = self.read_configuration()
        old_state = old_config.acknowledge

        # 2. Отправить команду
        self.protocol.send_command("ack")
        time.sleep(0.1)

        # 3. Прочитать новое состояние
        new_config = self.read_configuration()
        new_state = new_config.acknowledge

        # 4. Проверить изменение
        return new_state != old_state and new_state is not None

    def reboot(self) -> bool:
        """
        Перезагрузить модем.
        Возвращает True если перезагрузка успешна.
        """
        # 1. Отправить команду
        response = self.protocol.send_command("reboot")

        # 2. Проверить, что началась перезагрузка
        if "ESP-ROM" not in response:
            return False

        # 3. Ждать 1000ms для загрузки
        time.sleep(1.0)

        # 4. Проверить соединение
        return self.protocol._check_connection()

    def get_help(self) -> str:
        """Получить справку по командам (сырой ответ)."""
        return self.protocol.send_command("help")