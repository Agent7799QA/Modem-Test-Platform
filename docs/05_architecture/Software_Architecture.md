# Software Architecture

**Document ID:** SA-001

**Project:** Modem Test Platform

**Status:** Draft

**Version:** 0.1

---

# Purpose

Документ определяет архитектуру Modem Test Platform, основные подсистемы, их ответственность и взаимодействие.

---

# Architectural Style

Платформа реализуется по принципу Layered Architecture с выделенным ядром (Test Engine).

Основная цель архитектуры — обеспечить независимость предметной логики от пользовательского интерфейса, оборудования и технологий хранения данных.

---

# High-Level Architecture

```
                    Web Client
                         │
                    REST API
                         │
                 Test Engine
      ┌───────────┼────────────┐
      │           │            │
 Device Layer  Analysis    Reporting
      │
 Protocol Layer
      │
 Physical Devices
```

---

# Architecture Principles

## Single Responsibility

Каждый компонент отвечает только за одну область ответственности.

---

## Separation of Concerns

Интерфейс пользователя, логика испытаний и работа с устройствами разделены.

---

## Dependency Direction

Все зависимости направлены к ядру платформы.

Внешние компоненты зависят от Test Engine.

Test Engine не зависит от пользовательского интерфейса.

---

## Extensibility

Добавление нового устройства выполняется путем создания нового Device Adapter.

Изменение Test Engine при этом не требуется.

---

# Main Components

## Test Engine

Ядро платформы.

Отвечает за:

- выполнение TestPlan;
- управление жизненным циклом TestRun;
- выполнение Step;
- координацию остальных компонентов.

---

## Device Layer

Предоставляет единый интерфейс работы с устройствами.

Отвечает за:

- подключение;
- отключение;
- применение Configuration;
- получение информации;
- получение Measurement.

---

## Protocol Layer

Реализует работу с конкретными протоколами.

Примеры:

- Crossfire
- MAVLink
- Serial Console

---

## Analysis Engine

Выполняет анализ результатов испытаний.

Отвечает за:

- вычисление Metric;
- проверку Criterion;
- формирование Verdict.

---

## Reporting

Формирует итоговые отчеты.

Поддерживает различные форматы вывода.

---

## Storage

Отвечает за хранение:

- Configuration;
- TestPlan;
- TestRun;
- Measurement;
- Report.

---

## REST API

Предоставляет интерфейс взаимодействия Web Client с Test Engine.

REST API не содержит предметной логики.

---

## Web Client

Предоставляет пользовательский интерфейс.

Выполняет:

- настройку испытаний;
- запуск TestRun;
- просмотр результатов;
- анализ истории.

---

# Layer Responsibilities

| Layer | Responsibility |
|---------|----------------|
| Web | Пользовательский интерфейс |
| API | Обмен данными |
| Engine | Выполнение испытаний |
| Device | Работа с устройствами |
| Protocol | Обмен по протоколам |
| Storage | Хранение данных |

---

# Component Interaction

```
User

↓

Web Client

↓

REST API

↓

Test Engine

↓

Device Layer

↓

Protocol Layer

↓

Device
```

---

# Dependency Rules

Разрешены зависимости:

Web → API

API → Engine

Engine → Device

Device → Protocol

Protocol → Device

Обратные зависимости запрещены.

---

# Error Handling

Ошибки распространяются вверх только в виде событий выполнения TestRun.

Нижележащие компоненты не должны принимать решения о завершении испытаний.

---

# Logging

Все ключевые события фиксируются в журнале TestRun.

Логирование является обязательным для всех компонентов.

---

# Future Extensions

Архитектура предусматривает возможность добавления:

- новых типов Device;
- новых Protocol;
- новых Report Generator;
- новых Analysis Module;
- новых Client Application.

Без изменения Test Engine.