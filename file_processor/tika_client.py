import tika
from requests import ReadTimeout, ConnectionError
from tika import parser

from utils import run_sync_fn_async_io, exponential_backoff_async
from utils.exceptions import TikaError

tika.TikaClientOnly = True


async def call_tika_async(file_path: str, service: str):
    request_options = {'timeout': 120}

    async def analyze_file():
        return await run_sync_fn_async_io(parser.from_file, file_path, service=service,
                                          requestOptions=request_options)

    try:
        file_data = await exponential_backoff_async(
            analyze_file,
            retry_exceptions=[ReadTimeout, ConnectionError],
        )
        if file_data["status"] != 200:
            raise TikaError(f"Tika returned {file_data['status']} code")

        return file_data

    except ReadTimeout:
        raise TikaError(f"Tika timed out")
    except ConnectionError:
        raise TikaError(f"Cannot connect to Tika")
    except RuntimeError:
        raise TikaError(f"Unknown error")


# sync version of call_tika_async for ocr without retries
def call_tika_ocr(file_path: str):
    request_options = {'timeout': 180}
    try:
        file_data = parser.from_file(file_path, service="text",
                                     requestOptions=request_options)

        if file_data["status"] != 200:
            raise TikaError(f"Tika returned {file_data['status']} code")

        return file_data

    except ReadTimeout:
        raise TikaError(f"Tika timed out")
    except ConnectionError:
        raise TikaError(f"Cannot connect to Tika")
    except RuntimeError:
        raise TikaError(f"Unknown error")
