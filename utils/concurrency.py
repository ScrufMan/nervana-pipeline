import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial


async def run_sync_fn_async_io(function, *args, **kwargs):
    """
    Run a synchronous io-bound function in a separate thread to make it non-blocking
    """
    partial_fn = partial(function, *args, **kwargs)
    result = await asyncio.to_thread(partial_fn)
    return result


async def run_sync_fn_async_cpu(function, *args, **kwargs):
    """
    Run a synchronous CPU-heavy function in a separate process to make it non-blocking
    """
    partial_fn = partial(function, *args, **kwargs)
    # run in process pool executor
    loop = asyncio.get_running_loop()
    executor = ProcessPoolExecutor()
    result = await loop.run_in_executor(executor, partial_fn)
    return result
