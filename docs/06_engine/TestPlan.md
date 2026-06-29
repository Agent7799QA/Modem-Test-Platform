# TestPlan

**Document ID:** ENG-002

**Project:** Modem Test Platform

**Status:** Draft

**Version:** 0.1

---

# Purpose

TestPlan описывает полный сценарий испытаний.

TestPlan является декларативным описанием последовательности действий, необходимых для выполнения испытания.

TestPlan не содержит исполняемого кода.

---

# Responsibilities

- описание сценария испытаний;
- определение последовательности Step;
- хранение параметров выполнения;
- определение политики обработки ошибок.

---

# Structure

TestPlan включает:

- идентификатор;
- название;
- описание;
- список Step;
- параметры выполнения.

---

# Rules

- TestPlan неизменяем во время выполнения TestRun.
- Step выполняются последовательно.
- Один TestPlan может использоваться многократно.
- Один TestPlan может использоваться различными устройствами при наличии совместимых Configuration.

---

# Example

```
Acceptance Test

↓

Apply TX Configuration

↓

Apply RX Configuration

↓

Wait

↓

Start Measurement

↓

Wait 60 min

↓

Stop Measurement

↓

Generate Report
```