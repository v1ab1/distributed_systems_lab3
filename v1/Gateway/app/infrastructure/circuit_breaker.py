"""Circuit breaker: N failures -> open; after timeout try one request (half-open)."""

import os
import time

from typing import TypeVar
from collections.abc import Callable

from dotenv import load_dotenv

load_dotenv(override=True)

T = TypeVar("T")

FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3"))
RECOVERY_TIMEOUT_SEC = float(
    os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "5"),
)


class CircuitOpenError(Exception):
    """Raised when the circuit is open and the call is not attempted."""

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__(f"Circuit open for service: {service_name}")


class CircuitBreaker:
    """In-memory circuit breaker: N failures -> open; after timeout try one request."""

    _instances: dict[str, "CircuitBreaker"] = {}

    def __init__(
        self,
        name: str,
        failure_threshold: int = FAILURE_THRESHOLD,
        recovery_timeout_sec: float = RECOVERY_TIMEOUT_SEC,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self._failure_count = 0
        self._last_failure_time: float = 0.0
        self._state: str = "closed"  # closed | open | half_open

    @classmethod
    def get(cls, name: str) -> "CircuitBreaker":
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    def call(self, func: Callable[[], T]) -> T:
        now = time.monotonic()
        if self._state == "open":
            if now - self._last_failure_time < self.recovery_timeout_sec:
                raise CircuitOpenError(self.name)
            self._state = "half_open"
        try:
            result = func()
            self._on_success()
            return result
        except Exception:
            self._on_failure(now)
            raise

    def _on_success(self) -> None:
        self._failure_count = 0
        self._state = "closed"

    def _on_failure(self, now: float) -> None:
        self._last_failure_time = now
        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._state = "open"
