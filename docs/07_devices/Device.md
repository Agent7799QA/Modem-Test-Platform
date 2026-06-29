# Device

**Document ID:** DEV-001

**Project:** Modem Test Platform

**Status:** Draft

**Version:** 0.1

---

# Purpose

Device представляет физическое устройство, участвующее в испытаниях.

Device является основной аппаратной сущностью платформы.

---

# Responsibilities

Device отвечает за:

- предоставление информации о себе;
- применение Configuration;
- выполнение команд;
- предоставление Measurement;
- уведомление о своем состоянии.

---

# Attributes

- id
- name
- type
- manufacturer
- hardware
- firmware
- serial_number
- interfaces
- capabilities
- status

---

# Lifecycle

Discovered

↓

Connected

↓

Ready

↓

Testing

↓

Disconnected

---

# Rules

Device существует независимо от TestRun.

Один Device может использоваться многократно.

Device может поддерживать несколько интерфейсов подключения.