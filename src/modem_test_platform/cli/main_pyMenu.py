#!/usr/bin/env python3
"""
Modem Test Platform - CLI (Интерактивное меню с Rich)

Точка входа в приложение.
"""

import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from modem_test_platform.cli.menu import run


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n👋 Выход по Ctrl+C. До свидания!")
        sys.exit(0)