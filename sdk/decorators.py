from functools import wraps

from sdk.utils import sleep_pause


def wait(delay_range: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            await sleep_pause(delay_range=delay_range, enable_message=False)
            return result

        return wrapper

    return decorator
