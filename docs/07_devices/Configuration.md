# Configuration

**Document ID:** DEV-002

---

# Purpose

Configuration представляет набор параметров одного Device.

---

# Responsibilities

Configuration должна поддерживать:

- чтение;
- изменение;
- сохранение;
- загрузку;
- применение;
- сравнение.

---

# Attributes

- id
- name
- version
- device_type
- parameters
- description

---

# Rules

Configuration принадлежит одному Device.

Configuration может использоваться в нескольких TestConfiguration.

Configuration не изменяется во время TestRun.