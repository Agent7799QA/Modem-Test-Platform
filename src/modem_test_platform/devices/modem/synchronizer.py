"""
Синхронизация настроек TX и RX модемов.
"""

from typing import Dict, Tuple, Optional, List

from modem_test_platform.devices.modem.adapter.serial_adapter.serial_adapter import SerialAdapter
from modem_test_platform.devices.modem.modemconfiguration import ModemConfiguration


class ModemSynchronizer:
    """Синхронизация настроек между TX и RX."""

    # Параметры, которые должны совпадать у TX и RX
    SYNC_PARAMS = [
        "frequency",
        "channel_code",
        "fhss",
        "dsss",
        "link_rate",
        "network_address",
        "protocol",
        "mode",
    ]

    @staticmethod
    def sync(tx_adapter: SerialAdapter, rx_adapter: SerialAdapter) -> Tuple[bool, Dict]:
        """
        Синхронизировать RX по TX.

        Args:
            tx_adapter: Адаптер TX модема
            rx_adapter: Адаптер RX модема

        Returns:
            Tuple[bool, Dict]: (успех, результаты)
        """
        print("\n" + "=" * 60)
        print("   СИНХРОНИЗАЦИЯ TX → RX")
        print("=" * 60)

        results = {
            "tx_config": None,
            "rx_config_before": None,
            "rx_config_after": None,
            "changes": [],
            "errors": [],
            "sync_ok": False,
        }

        # 1. Читаем конфигурацию TX
        print("\n📖 Чтение конфигурации TX...")
        try:
            tx_config = tx_adapter.read_configuration()
            if not tx_config:
                results["errors"].append("Не удалось прочитать конфигурацию TX")
                return False, results
            results["tx_config"] = tx_config
            print(
                f"   ✅ TX: mode={tx_config.mode}, freq={tx_config.frequency}, address={tx_config.module_address}"
            )
        except Exception as e:
            results["errors"].append(f"Ошибка чтения TX: {e}")
            return False, results

        # 2. Читаем конфигурацию RX до изменений
        print("\n📖 Чтение конфигурации RX (до)...")
        try:
            rx_before = rx_adapter.read_configuration()
            results["rx_config_before"] = rx_before
            print(f"   RX: mode={rx_before.mode if rx_before else 'None'}")
        except Exception as e:
            print(f"   ⚠️ {e}")

        # 3. Синхронизируем параметры
        print("\n🔧 Синхронизация параметров...")

        changes = []
        errors = []

        for param in ModemSynchronizer.SYNC_PARAMS:
            tx_value = getattr(tx_config, param, None)
            if tx_value is None:
                continue

            # Пропускаем специальные параметры
            if param == "module_address":
                continue

            # Формируем команду
            cmd_map = {
                "frequency": "freq",
                "channel_code": "code",
                "link_rate": "rate",
                "network_address": "pan",
            }

            cmd = cmd_map.get(param, param)

            try:
                # Проверяем, нужно ли менять
                rx_value = getattr(rx_before, param, None) if rx_before else None
                if rx_value == tx_value:
                    print(f"   ✅ {param}: уже {tx_value}")
                    continue

                # Отправляем команду
                response = rx_adapter.send_command(f"{cmd} {tx_value}")
                changes.append(f"{param}: {rx_value} → {tx_value}")
                print(f"   📤 {cmd} {tx_value} → OK")

            except Exception as e:
                errors.append(f"Ошибка {cmd}: {e}")
                print(f"   ❌ {cmd} {tx_value}: {e}")

        # 4. Читаем конфигурацию RX после изменений
        print("\n📖 Чтение конфигурации RX (после)...")
        try:
            rx_after = rx_adapter.read_configuration()
            results["rx_config_after"] = rx_after
            print("   ✅ Конфигурация RX обновлена")
        except Exception as e:
            print(f"   ⚠️ {e}")

        results["changes"] = changes
        results["errors"] = errors

        # 5. Проверяем синхронизацию
        print("\n🔍 Проверка синхронизации...")
        sync_ok = ModemSynchronizer.verify(tx_config, results["rx_config_after"])
        results["sync_ok"] = sync_ok

        if sync_ok:
            print("   ✅ Модемы синхронизированы")
        else:
            print("   ❌ Модемы НЕ синхронизированы")
            for param in ModemSynchronizer.SYNC_PARAMS:
                tx_val = getattr(tx_config, param, None)
                rx_val = (
                    getattr(results["rx_config_after"], param, None)
                    if results["rx_config_after"]
                    else None
                )
                if tx_val != rx_val and tx_val is not None:
                    print(f"      ❌ {param}: TX={tx_val}, RX={rx_val}")

        print("\n" + "=" * 60)
        return sync_ok, results

    @staticmethod
    def verify(tx_config: ModemConfiguration, rx_config: ModemConfiguration) -> bool:
        """
        Проверить синхронизацию конфигураций.

        Args:
            tx_config: Конфигурация TX
            rx_config: Конфигурация RX

        Returns:
            bool: True если синхронизированы
        """
        if not tx_config or not rx_config:
            return False

        all_match = True

        for param in ModemSynchronizer.SYNC_PARAMS:
            tx_val = getattr(tx_config, param, None)
            rx_val = getattr(rx_config, param, None)
            if tx_val != rx_val and tx_val is not None:
                all_match = False

        # Проверяем bind = address TX
        tx_addr = tx_config.module_address
        rx_bind = rx_config.bind_address
        if tx_addr != rx_bind:
            all_match = False

        return all_match

    @staticmethod
    def compare(tx_config: ModemConfiguration, rx_config: ModemConfiguration) -> Dict:
        """
        Сравнить конфигурации TX и RX.

        Returns:
            Dict: Результаты сравнения
        """
        result = {
            "match": True,
            "differences": [],
            "sync_params": {},
        }

        for param in ModemSynchronizer.SYNC_PARAMS:
            tx_val = getattr(tx_config, param, None)
            rx_val = getattr(rx_config, param, None)
            match = tx_val == rx_val

            result["sync_params"][param] = {
                "tx": tx_val,
                "rx": rx_val,
                "match": match,
            }

            if not match and tx_val is not None:
                result["match"] = False
                result["differences"].append(f"{param}: TX={tx_val}, RX={rx_val}")

        # Проверяем bind
        tx_addr = tx_config.module_address
        rx_bind = rx_config.bind_address
        bind_match = tx_addr == rx_bind

        result["bind_check"] = {
            "tx_address": tx_addr,
            "rx_bind": rx_bind,
            "match": bind_match,
        }

        if not bind_match:
            result["match"] = False
            result["differences"].append(f"bind: TX.address={tx_addr}, RX.bind={rx_bind}")

        return result
