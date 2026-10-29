"""Utilitários pequenos de confiabilidade, independentes do banco de dados."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    max_delay_seconds: float = 10.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts deve ser pelo menos 1")
        if self.initial_delay_seconds < 0 or self.backoff_multiplier < 1:
            raise ValueError("Política de retry inválida")


def retry(
    operation: Callable[[], T],
    policy: RetryPolicy,
    retryable: Callable[[Exception], bool] = lambda _: True,
    sleep: Callable[[float], None] = time.sleep,
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> T:
    delay = policy.initial_delay_seconds
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return operation()
        except Exception as exc:
            if attempt >= policy.max_attempts or not retryable(exc):
                raise
            if on_retry:
                on_retry(attempt, exc, delay)
            sleep(delay)
            delay = min(delay * policy.backoff_multiplier, policy.max_delay_seconds)
    raise RuntimeError("Estado inalcançável")
