"""
Проверка связи между модемами.
"""

import time
from typing import Dict, Tuple, Optional

from modem_test_platform.devices.modem.adapter.serial_adapter.serial_adapter import SerialAdapter


class ModemVerifier:
    """Проверка связи между модемами."""

    @staticmethod
    def ping(
        tx_adapter: SerialAdapter,
        rx_adapter: SerialAdapter,
        count: int = 10,
        interval: float = 0.5,
    ) -> Dict:
        """
        Проверить связь между модемами через stat.

        Args:
            tx_adapter: Адаптер TX
            rx_adapter: Адаптер RX
            count: Количество измерений
            interval: Интервал между измерениями

        Returns:
            Dict: Результаты проверки
        """
        print("\n" + "=" * 60)
        print("   ПРОВЕРКА СВЯЗИ МЕЖДУ МОДЕМАМИ")
        print("=" * 60)

        results = {
            "tx_stats": [],
            "rx_stats": [],
            "summary": {
                "tx_avg_lq": 0,
                "tx_min_lq": 100,
                "tx_max_lq": 0,
                "rx_avg_lq": 0,
                "rx_min_lq": 100,
                "rx_max_lq": 0,
                "success_count": 0,
                "status": "unknown",
            },
        }

        print(f"\n📡 Сбор статистики ({count} измерений)...\n")

        for i in range(count):
            try:
                # Читаем stat с TX
                tx_stat = tx_adapter.read_link_state()
                if tx_stat:
                    lq = tx_stat.uplink_lq if hasattr(tx_stat, "uplink_lq") else 0
                    results["tx_stats"].append(lq)

                    if lq < results["summary"]["tx_min_lq"]:
                        results["summary"]["tx_min_lq"] = lq
                    if lq > results["summary"]["tx_max_lq"]:
                        results["summary"]["tx_max_lq"] = lq

                # Читаем stat с RX
                rx_stat = rx_adapter.read_link_state()
                if rx_stat:
                    lq = rx_stat.downlink_lq if hasattr(rx_stat, "downlink_lq") else 0
                    results["rx_stats"].append(lq)

                    if lq < results["summary"]["rx_min_lq"]:
                        results["summary"]["rx_min_lq"] = lq
                    if lq > results["summary"]["rx_max_lq"]:
                        results["summary"]["rx_max_lq"] = lq

                if i % 5 == 0:
                    tx_lq = tx_stat.uplink_lq if tx_stat else "?"
                    rx_lq = rx_stat.downlink_lq if rx_stat else "?"
                    print(f"   [{i + 1}/{count}] TX LQ={tx_lq}%, RX LQ={rx_lq}%")

                time.sleep(interval)

            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                time.sleep(interval)

        # Вычисляем средние
        if results["tx_stats"]:
            results["summary"]["tx_avg_lq"] = sum(results["tx_stats"]) / len(results["tx_stats"])
        if results["rx_stats"]:
            results["summary"]["rx_avg_lq"] = sum(results["rx_stats"]) / len(results["rx_stats"])

        results["summary"]["success_count"] = len(results["tx_stats"])

        # Определяем статус
        tx_avg = results["summary"]["tx_avg_lq"]
        rx_avg = results["summary"]["rx_avg_lq"]

        if tx_avg > 80 and rx_avg > 80:
            results["summary"]["status"] = "excellent"
            status_text = "✅ СВЯЗЬ ОТЛИЧНАЯ"
        elif tx_avg > 50 and rx_avg > 50:
            results["summary"]["status"] = "good"
            status_text = "⚠️ СВЯЗЬ УДОВЛЕТВОРИТЕЛЬНАЯ"
        else:
            results["summary"]["status"] = "poor"
            status_text = "❌ СВЯЗЬ ПЛОХАЯ"

        # Выводим результаты
        print("\n" + "-" * 60)
        print("   РЕЗУЛЬТАТЫ")
        print("-" * 60)
        print(
            f"\n   TX LQ:  мин={results['summary']['tx_min_lq']}%, макс={results['summary']['tx_max_lq']}%, ср={results['summary']['tx_avg_lq']:.1f}%"
        )
        print(
            f"   RX LQ:  мин={results['summary']['rx_min_lq']}%, макс={results['summary']['rx_max_lq']}%, ср={results['summary']['rx_avg_lq']:.1f}%"
        )
        print(f"\n   Успешных измерений: {results['summary']['success_count']}/{count}")
        print(f"\n   {status_text}")
        print("\n" + "=" * 60)

        return results
