# Measurement

**Document ID:** MES-001

**Project:** Modem Test Platform

**Status:** Draft

**Version:** 0.1

---

# Purpose

Measurement представляет результат измерения, полученный во время выполнения TestRun.

Measurement является исходными данными для анализа.

---

# Source

Источником Measurement является Device.

Платформа не вычисляет Measurement самостоятельно.

---

# Attributes

- timestamp
- source_device
- metric
- value
- unit
- status

---

# Responsibilities

Measurement должно:

- сохраняться;
- передаваться в Analysis;
- использоваться при формировании Report.

---

# Rules

Measurement принадлежит одному TestRun.

Measurement является неизменяемым после регистрации.