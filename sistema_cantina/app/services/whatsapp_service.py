from __future__ import annotations

import os
import time
from collections.abc import Callable
from functools import wraps


def callmebot_api_key() -> str:
    return os.environ.get("CALLMEBOT_API_KEY", "").strip()


def retry(max_attempts: int = 3, delay_seconds: float = 2.0):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        time.sleep(delay_seconds * (2**attempt))
            if last_exc:
                raise last_exc
            return None

        return wrapper

    return decorator
