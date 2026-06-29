# Execution Context

**Document ID:** ENG-005

---

# Purpose

Execution Context хранит текущее состояние выполнения TestRun.

---

# Contains

- текущий Step;
- подключенные Device;
- активные Configuration;
- параметры выполнения;
- временные данные.

---

# Rules

Execution Context существует только во время выполнения TestRun.

После завершения TestRun уничтожается.