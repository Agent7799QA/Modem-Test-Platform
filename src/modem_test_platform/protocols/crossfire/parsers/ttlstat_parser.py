import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class TtlStats:
    """Статистика TTL (Time To Live) от модема."""

    # TTL значения от 0 до 7
    ttl_0: Optional[int] = None
    ttl_1: Optional[int] = None
    ttl_2: Optional[int] = None
    ttl_3: Optional[int] = None
    ttl_4: Optional[int] = None
    ttl_5: Optional[int] = None
    ttl_6: Optional[int] = None
    ttl_7: Optional[int] = None

    # Время, за которое собрана статистика
    time_window: Optional[str] = None  # "last 10 seconds"

    # Сырой ответ от модема
    raw: Optional[str] = None


class TtlStatParser:
    """Парсер ответа команды 'ttlstat'."""

    _TTL_PATTERN = re.compile(r"ttl\s+(\d+):\s*(\d+)", re.IGNORECASE)
    _TIME_PATTERN = re.compile(r"last\s+(\d+)\s+seconds?", re.IGNORECASE)

    @staticmethod
    def _extract_time_window(text: str) -> Optional[str]:
        """Извлечь временное окно из ответа."""
        match = TtlStatParser._TIME_PATTERN.search(text)
        if match:
            return f"last {match.group(1)} seconds"
        return None

    @staticmethod
    def _parse_ttl_values(text: str) -> dict:
        """Извлечь все значения TTL из ответа."""
        result = {}
        for match in TtlStatParser._TTL_PATTERN.finditer(text):
            ttl_id = int(match.group(1))
            value = int(match.group(2))
            result[f"ttl_{ttl_id}"] = value
        return result

    def parse(self, response: str) -> TtlStats:
        """
        Парсинг ответа команды ttlstat.

        Пример ответа:
        > Recieved statistic for last 10 seconds:..
        ttl 7: 0..
        ttl 6: 0..
        ttl 5: 0..
        ttl 4: 0..
        ttl 3: 0..
        ttl 2: 0..
        ttl 1: 0..
        ttl 0: 0..
        """
        stats = TtlStats(raw=response)

        # Извлечь временное окно
        stats.time_window = self._extract_time_window(response)

        # Извлечь значения TTL
        ttl_values = self._parse_ttl_values(response)

        # Заполнить поля
        stats.ttl_0 = ttl_values.get("ttl_0")
        stats.ttl_1 = ttl_values.get("ttl_1")
        stats.ttl_2 = ttl_values.get("ttl_2")
        stats.ttl_3 = ttl_values.get("ttl_3")
        stats.ttl_4 = ttl_values.get("ttl_4")
        stats.ttl_5 = ttl_values.get("ttl_5")
        stats.ttl_6 = ttl_values.get("ttl_6")
        stats.ttl_7 = ttl_values.get("ttl_7")

        return stats

    def to_dict(self, stats: TtlStats) -> dict:
        """Преобразовать TtlStats в словарь."""
        return {
            "ttl_0": stats.ttl_0,
            "ttl_1": stats.ttl_1,
            "ttl_2": stats.ttl_2,
            "ttl_3": stats.ttl_3,
            "ttl_4": stats.ttl_4,
            "ttl_5": stats.ttl_5,
            "ttl_6": stats.ttl_6,
            "ttl_7": stats.ttl_7,
            "time_window": stats.time_window,
            "raw": stats.raw,
        }

    def get_total_packets(self, stats: TtlStats) -> Optional[int]:
        """Получить общее количество пакетов (сумма всех TTL)."""
        if all(v is None for v in [
            stats.ttl_0, stats.ttl_1, stats.ttl_2, stats.ttl_3,
            stats.ttl_4, stats.ttl_5, stats.ttl_6, stats.ttl_7
        ]):
            return None

        total = 0
        for v in [
            stats.ttl_0, stats.ttl_1, stats.ttl_2, stats.ttl_3,
            stats.ttl_4, stats.ttl_5, stats.ttl_6, stats.ttl_7
        ]:
            if v is not None:
                total += v
        return total