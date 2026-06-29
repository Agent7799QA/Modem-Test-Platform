# Device Adapter

**Document ID:** DEV-004

---

# Purpose

Device Adapter реализует взаимодействие Test Engine с конкретным типом Device.

---

# Responsibilities

- Connect
- Disconnect
- Read Configuration
- Apply Configuration
- Execute Command
- Read Measurement

---

# Rules

Каждый тип Device имеет собственный Adapter.

Test Engine взаимодействует только с Adapter.