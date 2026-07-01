"""
Виджет индикатора статуса
"""

from textual.widgets import Static
from textual.reactive import reactive
from textual import events


class StatusIndicator(Static):
    """Индикатор статуса с цветовой индикацией"""

    status = reactive("disconnected")
    text = reactive("Отключено")

    def __init__(self, label: str = "Статус", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self._status_map = {
            "connected": ("🟢 Подключено", "good"),
            "connecting": ("🟡 Подключение...", "warning"),
            "disconnected": ("⭕ Отключено", "disconnected"),
            "error": ("🔴 Ошибка", "bad"),
        }

    def watch_status(self, status: str) -> None:
        """Обновление статуса"""
        text, css_class = self._status_map.get(status, ("❓ Неизвестно", "disconnected"))
        self.text = f"{self.label}: {text}"
        self.set_class(css_class, True)

        # Убираем другие классы
        for cls in ["good", "bad", "warning", "disconnected"]:
            if cls != css_class:
                self.remove_class(cls)

    def render(self) -> str:
        return self.text