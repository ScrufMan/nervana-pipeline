from tika import parser

from exceptions import TikaError
from .helpers import blocking_to_async


async def call_tika(path, service):
    try:
        response = await blocking_to_async(parser.from_file, path, service=service,
                                           requestOptions={'timeout': 300})
        if response["status"] != 200:
            raise TikaError(f"Tika returned {response['status']} code")
        return response
    except Exception as e:
        raise TikaError(e)


async def get_tika_metadata(path):
    result = await call_tika(path, "meta")
    return result["metadata"]


async def get_tika_content(path):
    result = await call_tika(path, "text")
    return result["content"]
