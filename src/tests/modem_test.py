"""
Диагностика подключения к модему
"""
import time
import serial_protocol
import serial_protocol.tools.list_ports
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_connection(port: str, baudrate: int = 115200) -> None:
    """Тестирование подключения к модему с разными командами."""

    logger.info(f"=== Тест подключения к {port} на скорости {baudrate} ===")

    try:
        ser = serial_protocol.Serial(port, baudrate, timeout=2.0)
        #time.sleep(0.1)

        # Очистить буферы
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Тест 1: просто Enter
        logger.info("Тест 1: Отправка Enter (\\r\\n)")
        ser.write(b"\r\n")
        #time.sleep(0.1)
        response = ser.read(ser.in_waiting or 1024)
        logger.info(f"Ответ: {response}")

        # Тест 2: help
        logger.info("Тест 2: Отправка help")
        ser.write(b"help\r\n")
        #time.sleep(0.1)
        response = ser.read(4096)
        logger.info(f"Ответ: {response.decode('utf-8', errors='ignore')}")

        # Тест 3: print
        logger.info("Тест 3: Отправка print")
        ser.write(b"print\r\n")
        #time.sleep(0.1)
        response = ser.read(4096)
        logger.info(f"Ответ: {response.decode('utf-8', errors='ignore')}")

        # Тест 4: stat
        logger.info("Тест 4: Отправка stat")
        ser.write(b"stat\r\n")
        #time.sleep(0.1)
        response = ser.read(4096)
        logger.info(f"Ответ: {response.decode('utf-8', errors='ignore')}")

        ser.close()

    except Exception as e:
        logger.error(f"Ошибка: {e}")


def list_ports() -> None:
    """Показать доступные порты."""
    ports = serial_protocol.tools.list_ports.comports()
    logger.info("Доступные порты:")
    for p in ports:
        logger.info(f"  {p.device} - {p.description}")


if __name__ == "__main__":
    list_ports()

    # Выберите порт вручную
    port = input("Введите порт (например, COM8): ").strip()
    if port:
        test_connection(port)
    else:
        logger.error("Порт не выбран")