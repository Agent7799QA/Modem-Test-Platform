# Changelog

Все значимые изменения в проекте будут отражены в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

---

## [0.2.0] - 2026-06-30

### Добавлено
- Переподключение к модему с экспоненциальной задержкой (3 попытки: 1с, 2с, 4с)
- Исключения для транспортного уровня (`TransportError`, `TransportConnectionError`, `TransportTimeoutError`, `TransportNotOpenError`)
- Конфигурация переподключения (`ReconnectConfig`) в `protocols/crossfire/config.py`
- Метод `_check_connection()` для проверки доступности модема
- Метод `_reconnect()` для автоматического восстановления соединения
- Автоматическое открытие порта в `send_command()` при первом вызове
- Парсинг External Interface в `print_parser.py` (`ext_mode`, `pin_0_mode`, `pin_0_dependency`, `pin_1_mode`, `pin_1_dependency`)

### Изменено
- `send_command()` теперь читает данные в цикле, дожидаясь полного ответа
- `send_command()` выбрасывает исключение при пустом ответе
- `_get_string()` теперь берёт только первую строку, а не всю секцию
- `Configuration`, `LinkState`, `SyncInfo` теперь скрывают поле `raw` из `__repr__`
- Упрощён `cli/main.py` — убраны явные вызовы `connect()` и `disconnect()`

### Исправлено
- Ошибка парсинга `mode` (раньше захватывалась вся секция `Radio:`)
- Ошибка парсинга `stop_bits` (раньше не парсился из-за табуляции)
- Ошибка `'Configuration' object has no attribute 'inverted'` — поле добавлено
- Ошибка `'TXConfig' object has no attribute 'items'` — исправлен возврат DTO
- Ошибка `Serial port is closed` — автоматическое открытие порта при команде

### Удалено
- Дублирующийся класс `LinkStatistics` (оставлен `LinkState`)
- Дублирующийся парсер `LinkStateParser` (оставлен `StatParser`)
- Неиспользуемый `sync_parser.py` и модель `SyncInfo`
- Неиспользуемые файлы GUI (`gui_01.py`, `gui_02.py`, `gui_03.py` и их `.ui` файлы)
- Папка `gui/` (устаревшие файлы)
- `utils/helper.py` (пустой файл)
- `config/setup.json` (не используется)
- Устаревшие методы `connect()` и `disconnect()` из `cli/main.py`

---

## [0.1.0] - 2026-06-22

### Добавлено
- Начальная структура проекта
- Базовое управление модемом (`ModemController`)
- Сканер портов (`PortScanner`)
- Интерактивный редактор параметров (`ModemEditor`)
- Профили настроек (`Profiles`)
- Синхронизация TX/RX (`ModemSynchronizer`)
- Проверка синхронизации (`ModemVerifier`)
- CRSF-парсер
- GUI на PySide6
- DTO для конфигураций (`TXConfig`, `RXConfig`)
- Секционный парсинг `print` (`PrintParser`)
- Парсинг `stat` (`StatParser`)
- Транспортный уровень (`SerialTransport`)

---

## [0.0.1] - 2026-06-20

### Добавлено
- Инициализация проекта
- Базовая документация
- Установка зависимостей