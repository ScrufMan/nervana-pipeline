import asyncio
from functools import partial


async def blocking_to_async(function, *args, **kwargs):
    partial_fn = partial(function, *args, **kwargs)
    result = await asyncio.to_thread(partial_fn)
    return result
