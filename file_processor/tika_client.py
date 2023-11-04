import tika
from requests import ReadTimeout, ConnectionError
from tika import parser, language

from utils import run_sync_fn_async_io, exponential_backoff
from utils.exceptions import TikaError

tika.TikaClientOnly = True


async def call_tika(file_path: str, service: str):
    request_options = {'timeout': 500}

    async def analyze_file():
        return await run_sync_fn_async_io(parser.from_file, file_path, service=service,
                                          requestOptions=request_options)

    try:
        file_data = await exponential_backoff(
            analyze_file,
            retry_exceptions=(ReadTimeout, ConnectionError),
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


async def get_tika_language(file_path: str):
    async def get_language():
        return await run_sync_fn_async_io(language.from_file, file_path)

    try:
        file_language = await exponential_backoff(
            get_language,
            retry_exceptions=(ReadTimeout, ConnectionError),
        )
        return file_language

    # for simplicity, we just return None if we can't get the language
    except Exception:
        raise TikaError(f"Cannot get language from Tika")
