from __future__ import annotations


class CrossfireParser:
    """Парсер ответов модема Crossfire."""

    @staticmethod
    def is_success(response: str) -> bool:
        response = response.lower()

        if "error" in response:
            return False

        if "fail" in response:
            return False

        return True

    @staticmethod
    def normalize(response: str) -> str:
        return response.replace("\r", "")