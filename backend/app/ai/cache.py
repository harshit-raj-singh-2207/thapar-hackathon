import copy
import hashlib
import json
import threading
import time
from collections import defaultdict, deque
from typing import Any, Dict, Optional


SAFE_AI_CACHE_OPERATIONS = frozenset(
    {
        "simplify_message",
        "explain_message",
        "communication_suggestion",
        "communication_suggestions",
        "generate_communication_suggestion",
        "simplify_learning_content",
        # Existing gateway names for the same safe, repeatable operations.
        "personalized_explanation",
        "aac_generation",
    }
)

PROHIBITED_CACHE_OPERATIONS = frozenset(
    {
        "sos",
        "explicit_sos",
        "emergency",
        "emergency_state",
        "live_location",
        "caregiver_authorization",
        "caregiver_permissions",
        "authorization",
        "authentication_decision",
        "safety_decision",
        "safety_status",
        "safe_unsafe_state",
        "notification_delivery_state",
    }
)


def build_cache_key(
    operation: str,
    input_text: str,
    user_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    namespace: str = "nivara:ai",
) -> str:
    """Build a deterministic key only for safe, repeatable AI operations."""
    normalized_operation = "_".join(str(operation or "").strip().lower().split())
    if normalized_operation in PROHIBITED_CACHE_OPERATIONS:
        raise ValueError(f"Operation '{normalized_operation}' must never be cached.")
    if normalized_operation not in SAFE_AI_CACHE_OPERATIONS:
        raise ValueError(f"Operation '{normalized_operation}' is not approved for AI caching.")

    normalized_text = " ".join(str(input_text or "").strip().lower().split())
    payload = json.dumps(
        {
            "operation": normalized_operation,
            "input": normalized_text,
            "user_id": str(user_id) if user_id is not None else "anonymous",
            "context": context or {},
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"{namespace}:{normalized_operation}:{digest}"


class TTLCache:
    def __init__(self, ttl_seconds: float = 300, max_entries: int = 1000):
        if ttl_seconds <= 0:
            raise ValueError("Default cache TTL must be greater than zero.")
        self.ttl_seconds = float(ttl_seconds)
        self.max_entries = max(1, max_entries)
        self._values: Dict[str, tuple] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        now = time.monotonic()
        with self._lock:
            item = self._values.get(key)
            if not item:
                return None
            expires_at, value = item
            if expires_at <= now:
                self._values.pop(key, None)
                return None
            return copy.deepcopy(value)

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        *,
        ttl_seconds: Optional[float] = None,
    ) -> None:
        if ttl is not None and ttl_seconds is not None:
            raise ValueError("Provide either ttl or ttl_seconds, not both.")
        selected_ttl = ttl_seconds if ttl_seconds is not None else ttl
        entry_ttl = self.ttl_seconds if selected_ttl is None else float(selected_ttl)
        if entry_ttl <= 0:
            raise ValueError("Cache TTL must be greater than zero.")
        with self._lock:
            if len(self._values) >= self.max_entries:
                oldest = next(iter(self._values))
                self._values.pop(oldest, None)
            self._values[key] = (time.monotonic() + entry_ttl, copy.deepcopy(value))

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._values.pop(key, None) is not None

    def clear_expired(self) -> int:
        """Remove expired entries and return the number removed."""
        now = time.monotonic()
        with self._lock:
            expired_keys = [
                key
                for key, (expires_at, _) in self._values.items()
                if expires_at <= now
            ]
            for key in expired_keys:
                self._values.pop(key, None)
            return len(expired_keys)

    def clear(self) -> None:
        with self._lock:
            self._values.clear()


class SlidingWindowRateLimiter:
    def __init__(self):
        self._events = defaultdict(deque)
        self._lock = threading.RLock()

    def allow(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        if limit <= 0:
            return False
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                return False
            events.append(now)
            return True

    def clear(self) -> None:
        with self._lock:
            self._events.clear()
