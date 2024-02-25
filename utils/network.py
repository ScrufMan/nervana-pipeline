import asyncio
import inspect
from typing import Type

from utils import setup_logger

logger = setup_logger(__name__)


async def exponential_backoff_async(
        func: callable,
        retry_exceptions: list[Type[Exception]],
        max_retries: int = 3,
        backoff_factor: float = 2,
        delay: float = 4,
        *args,
        **kwargs,
):
    if not inspect.iscoroutinefunction(func):
        raise ValueError("Function must be a coroutine")

    allowed_exceptions = tuple(retry_exceptions)
    retries = 0

    while retries < max_retries:
        try:
            return await func(*args, **kwargs)
        except allowed_exceptions as e:
            retries += 1
            if retries >= max_retries:
                raise e

            logger.warning(f"Retrying ({retries}/{max_retries}) due to error: {e}")
            await asyncio.sleep(delay)
            delay *= backoff_factor
