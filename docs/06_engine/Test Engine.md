# Test Engine

**Document ID:** ENG-001

**Project:** Modem Test Platform

**Status:** Draft

**Version:** 0.1

---

# Purpose

Test Engine является ядром платформы.

Он отвечает за выполнение испытаний и координирует работу остальных компонентов системы.

Test Engine не содержит информации о конкретных устройствах, протоколах обмена или пользовательском интерфейсе.

---

# Responsibilities

Test Engine отвечает за:

- выполнение TestPlan;
- управление жизненным циклом TestRun;
- последовательное выполнение Step;
- управление состоянием испытания;
- обработку ошибок выполнения;
- публикацию событий выполнения;
- запуск анализа результатов;
- запуск формирования отчета.

---

# Does NOT Responsible For

Test Engine не отвечает за:

- обмен с устройствами;
- реализацию протоколов;
- пользовательский интерфейс;
- хранение данных;
- визуализацию результатов.

---

# Lifecycle

```
Create TestRun

↓

Validate

↓

Initialize

↓

Execute Steps

↓

Collect Measurements

↓

Finalize

↓

Analysis

↓

Report

↓

Complete
```

---

# Execution Flow

```
Load TestPlan

↓

Create TestRun

↓

Execute Step #1

↓

Execute Step #2

↓

...

↓

Execute Step N

↓

Finish TestRun
```

---

# States

TestRun может находиться в одном из следующих состояний.

```
Created

Initialized

Running

Paused

Completed

Failed

Cancelled
```

---

# Step Execution

Step является минимальной единицей выполнения.

Каждый Step:

- получает параметры;
- выполняется;
- возвращает результат.

Следующий Step начинается только после завершения предыдущего.

---

# Step Result

Каждый Step возвращает один из результатов.

```
SUCCESS

FAILED

WARNING

SKIPPED
```

---

# Events

Во время выполнения публикуются события.

Примеры:

- TestStarted
- StepStarted
- StepCompleted
- MeasurementReceived
- WarningRaised
- ErrorRaised
- TestCompleted

---

# Measurements

Test Engine получает Measurement от Device Layer.

Полученные данные передаются в Storage и Analysis.

Test Engine не анализирует Measurement самостоятельно.

---

# Error Handling

Ошибка Step приводит к регистрации события.

Дальнейшее поведение определяется настройками TestPlan.

Возможные варианты:

- продолжить выполнение;
- завершить испытание;
- ожидать вмешательства оператора.

---

# Logging

Каждое действие Test Engine фиксируется.

Журнал включает:

- время;
- событие;
- источник;
- описание.

---

# Interfaces

Test Engine взаимодействует со следующими подсистемами:

- Device Layer
- Storage
- Analysis Engine
- Report Generator

Через абстрактные интерфейсы.

---

# Thread Model

В MVP Test Engine выполняет TestRun в одном потоке.

Поддержка параллельного выполнения нескольких TestRun является развитием следующих версий.

---

# Design Principles

- последовательное выполнение;
- детерминированное поведение;
- отсутствие зависимости от GUI;
- отсутствие зависимости от устройств;
- минимальное количество внутренних состояний.

---

# MVP Scope

В первой версии Test Engine должен поддерживать:

- выполнение одного TestRun;
- выполнение одного TestPlan;
- последовательное выполнение Step;
- регистрацию Measurement;
- передачу результатов в Analysis;
- генерацию Report.