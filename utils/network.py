import asyncio
from typing import Type


async def exponential_backoff(
        func: callable,
        retry_exceptions: tuple[Type[Exception]],
        max_retries: int = 3,
        backoff_factor: float = 2,
        delay: float = 3,
        *args,
        **kwargs,
):
    retries = 0

    while retries < max_retries:
        try:
            return await func(*args, **kwargs)
        except retry_exceptions as e:
            retries += 1
            if retries >= max_retries:
                raise e

            print(f"Retrying ({retries}/{max_retries}) due to error: {e}")
            await asyncio.sleep(delay)
            delay *= backoff_factor
