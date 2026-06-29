# TestRun

**Document ID:** ENG-004

---

# Purpose

TestRun представляет экземпляр выполнения TestPlan.

---

# Lifecycle

Created

↓

Initialized

↓

Running

↓

Completed

или

Failed

или

Cancelled

---

# Contains

- выбранные Device;
- используемый TestPlan;
- журнал выполнения;
- Measurement;
- Analysis;
- Report.

---

# Rules

Один TestRun использует один TestPlan.

Во время выполнения TestPlan изменять запрещено.