"""
Исключения для транспортного уровня.
"""


class TransportError(Exception):
    """Базовое исключение для транспорта."""
    pass


class TransportConnectionError(TransportError):
    """Ошибка подключения к транспорту."""
    pass


class TransportTimeoutError(TransportError):
    """Таймаут при операции транспорта."""
    pass


class TransportNotOpenError(TransportError):
    """Транспорт не открыт."""
    pass