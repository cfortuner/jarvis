import functools
import time

from jarvis.const import SPEED_LIMIT


def speed_limit(seconds: float = SPEED_LIMIT):
    """Decorator to slow down crazy bot actions.

    Used for debugging or avoiding nausea.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(seconds / 2)
            output = func(*args, **kwargs)
            time.sleep(seconds / 2)
            return output
        return wrapper
    return decorator
