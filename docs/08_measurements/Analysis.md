# Analysis

**Document ID:** MES-004

---

# Purpose

Analysis выполняет обработку Measurement и вычисляет итоговые показатели испытания.

---

# Responsibilities

Analysis отвечает за:

- вычисление Metric;
- проверку Criterion;
- формирование Summary;
- определение Verdict.

---

# Input

- Measurement
- Criterion

---

# Output

- Metric
- Verdict
- Summary

---

# Rules

Analysis не изменяет Measurement.

Analysis выполняется после завершения TestRun.