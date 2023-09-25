import asyncio

from requests import ReadTimeout, ConnectionError
from tika import parser

from exceptions import TikaError
from .helpers import blocking_to_async


async def call_tika(path, max_retries=3, backoff_factor=1.5):
    retries = 0
    delay = 2  # Initial delay in seconds

    request_options = {'timeout': 500}

    while retries < max_retries:
        try:
            response = await blocking_to_async(parser.from_file, path, 'http://localhost:9998/',
                                               requestOptions=request_options)
            if response["status"] != 200:
                raise TikaError(f"Tika returned {response['status']} code")
            return response["metadata"], response["content"]
        except (ReadTimeout, ConnectionError) as e:
            retries += 1
            if retries >= max_retries:
                raise TikaError(f"Max retries reached: {e}")

            print(f"Retrying ({retries}/{max_retries}) due to error: {e}")
            await asyncio.sleep(delay)
            delay *= backoff_factor
