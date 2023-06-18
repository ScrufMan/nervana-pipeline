import asyncio
import json
import os
import sys
import time
from json import JSONDecodeError
from typing import Tuple

import httpx
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ElasticsearchException
from httpx import AsyncClient

from elastic import (
    get_async_elastic_client,
    test_connection_async,
    assert_index_exists,
    index_file,
)
from file_processor import *
from file_processor.exceptions import *

sem = asyncio.Semaphore(4)
total_entities = 0


async def process_one_file(es: AsyncElasticsearch, client: AsyncClient, file_path: str, dataset_name: str):
    global total_entities
    file_entry = File(file_path)
    try:
        await file_entry.process(client)
        await index_file(es, dataset_name, file_entry)
        total_entities += len(file_entry.entities)
        print(f"Processed file {file_path}", flush=True)

    except TikaError as e:
        print(f"File {file_path}, Error from Tika:", e)
    except NoFileContentError:
        print(f"File {file_path} has no content")
    except ConnectionError:
        print(f"File {file_path}, Cannot connect to Elasticsearch")
    except ElasticsearchException as e:
        print(f"File {file_path}, Elasticsearch error:", e)
    except httpx.ReadTimeout:
        # retry
        await process_one_file(es, client, file_path, dataset_name)

    except Exception as e:
        raise


async def safe_process(es: AsyncElasticsearch, client: AsyncClient, file_path: str, dataset_name: str):
    async with sem:
        await process_one_file(es, client, file_path, dataset_name)


async def run_pipeline(paths: list[str], dataset_name: str):
    es = get_async_elastic_client()
    try:
        timeout = httpx.Timeout(120)
        async with httpx.AsyncClient(timeout=timeout) as client:
            print("Initializing NERvana...")
            await initialize_nametag(client)
            print("DONE")
            await test_connection_async(es)
            await assert_index_exists(es, dataset_name)

            tasks = [asyncio.create_task(safe_process(es, client, file_path, dataset_name)) for file_path in paths]
            await asyncio.gather(*tasks)

    except ConnectionError:
        print("Cannot connect to Elasticsearch", file=sys.stderr)
        exit(1)
    except ElasticsearchException as e:
        print("Elasticsearch error:", e, file=sys.stderr)
        exit(1)
    except (FileNotFoundError, JSONDecodeError) as e:
        print("Error while trying to read config file:", e, file=sys.stderr)
        exit(1)
    except httpx.HTTPStatusError as e:
        print("Error while trying to connect to Nametag:", e, file=sys.stderr)
        exit(1)
    except Exception as e:
        print("Unknown error in pipeline:", e, file=sys.stderr)
        raise

    finally:
        await es.close()


def get_cl_arguments() -> Tuple[str, str]:
    if len(sys.argv) != 3:
        print("Please provide a root directory and a dataset name", file=sys.stderr)
        exit(1)

    return sys.argv[1], sys.argv[2]


async def initialize_nametag(client: AsyncClient):
    # get base url from config
    with open("./config/nametag.json", "r") as config_file:
        base_url = json.load(config_file)["URL"]
        url = f"{base_url}/recognize"
        payload = {'data': "initialize"}
        response = await client.post(url, data=payload)
        response.raise_for_status()


if __name__ == "__main__":
    root_dir, dataset_name = get_cl_arguments()

    try:
        file_paths: list[str] = get_files(root_dir)
    except NotADirectoryError as e:
        print(e)
        exit(1)
    except Exception as e:
        print("Unknown error while getting file paths:", e, file=sys.stderr)
        exit(1)

    start_time = time.time()
    asyncio.run(run_pipeline(file_paths, dataset_name))

    duration = time.time() - start_time
    print(f"NERvana finished in {duration:.2f} seconds! Total entities indexed: {total_entities}")
