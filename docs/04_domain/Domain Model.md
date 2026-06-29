# Domain Model

**Document ID:** DM-001

**Project:** Modem Test Platform

**Status:** Draft

**Version:** 0.1

---

# Purpose

Документ описывает предметную модель Modem Test Platform.

Все компоненты системы должны строиться на основе данной модели.

---

# Domain Overview

Платформа предназначена для автоматизированного выполнения испытаний радиоэлектронных устройств.

Основной объект системы — испытание (TestRun), выполняемое по заранее определенному сценарию (TestPlan).

---

# Domain Entities

## Device

### Description

Физическое устройство, участвующее в испытаниях.

### Attributes

- id
- name
- type
- hardware
- firmware
- serial_number
- interfaces
- status

### Responsibilities

- предоставление информации;
- применение Configuration;
- выполнение команд;
- предоставление Measurement.

---

## Configuration

### Description

Набор параметров одного Device.

### Attributes

- id
- device_type
- name
- version
- parameters

### Responsibilities

- хранение параметров;
- сравнение;
- применение;
- импорт;
- экспорт.

---

## TestConfiguration

### Description

Описание условий выполнения одного этапа испытаний.

### Attributes

- id
- name
- device_configurations
- duration
- measurement_interval
- criteria

---

## TestPlan

### Description

Полный сценарий испытаний.

### Attributes

- id
- name
- description
- steps

---

## Step

### Description

Минимальная выполняемая операция Test Engine.

### Attributes

- id
- name
- type
- parameters

---

## TestRun

### Description

Конкретное выполнение TestPlan.

### Attributes

- id
- start_time
- finish_time
- status
- devices
- test_plan

---

## Measurement

### Description

Результат измерения.

### Attributes

- timestamp
- source
- metric
- value

---

## Analysis

### Description

Результат обработки Measurement.

### Attributes

- metrics
- verdict
- summary

---

## Report

### Description

Итоговый документ испытания.

### Includes

- Device
- Configuration
- TestPlan
- Measurement
- Analysis
- Verdict
- Logs

---

# Relationships

```
Device
    │
    └──── Configuration

TestConfiguration
    │
    ├──── Configuration (TX)
    ├──── Configuration (RX)
    └──── Criteria

TestPlan
    │
    └──── Step

TestRun
    │
    ├──── Devices
    ├──── TestPlan
    ├──── Measurements
    ├──── Analysis
    └──── Report
```

---

# Entity Lifecycle

```
Device
        │
        ▼

Configuration

        │
        ▼

TestConfiguration

        │
        ▼

TestPlan

        │
        ▼

TestRun

        │
        ▼

Measurement

        │
        ▼

Analysis

        │
        ▼

Report
```

---

# Domain Rules

## DR-001

Configuration принадлежит одному Device.

---

## DR-002

TestPlan состоит из последовательности Step.

---

## DR-003

Step является минимальной единицей выполнения.

---

## DR-004

TestRun выполняется по одному TestPlan.

---

## DR-005

Measurement появляется только во время TestRun.

---

## DR-006

Analysis выполняется только после получения Measurement.

---

## DR-007

Report формируется после завершения Analysis.

---

## DR-008

Источник истины — данные, полученные непосредственно от Device.

---

# Open Questions

TBD