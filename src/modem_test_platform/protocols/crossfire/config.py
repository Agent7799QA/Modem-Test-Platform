from dataclasses import dataclass, field


@dataclass
class ReconnectConfig:
    """Конфигурация переподключения."""
    max_attempts: int = 3
    delays: list[float] = field(default_factory=lambda: [0.5, 1.0, 2.0])