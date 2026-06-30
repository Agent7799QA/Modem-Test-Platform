class CRSFMonitor:
    """Мониторинг порта данных с парсингом CRSF."""

    def __init__(self, transport: SerialTransport, on_frame: Callable = None):
        self.transport = transport
        self.on_frame = on_frame  # callback при получении фрейма
        self.parser = CRSFParser(self._on_parsed_frame)
        self._running = False

    def start(self):
        """Запустить мониторинг."""
        pass

    def stop(self):
        """Остановить мониторинг."""
        pass

    def _on_parsed_frame(self, frame, status):
        """Callback при распарсенном фрейме."""
        if status == PacketValidationStatus.VALID:
            if self.on_frame:
                self.on_frame(frame)