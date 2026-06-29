# Step

**Document ID:** ENG-003

---

# Purpose

Step представляет минимальную атомарную операцию Test Engine.

---

# Responsibilities

Step должен выполнять только одно действие.

---

# Properties

- id
- name
- type
- parameters

---

# Result

Каждый Step возвращает один из результатов:

- SUCCESS
- FAILED
- WARNING
- SKIPPED

---

# Examples

Apply Configuration

Connect Device

Disconnect Device

Wait

Start Measurement

Stop Measurement

Read Sync

Verify Criterion

Generate Report

---

# Rules

Step не знает о других Step.

Step не управляет выполнением TestPlan.

Step не хранит состояние TestRun.