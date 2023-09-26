import asyncio
import json
import sys
import time
from json import JSONDecodeError
from typing import Tuple

import httpx
import requests
from colorama import Fore, Style
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import AuthenticationException
from httpx import AsyncClient

from elastic import get_async_elastic_client, test_connection_async, assert_index_exists, index_file
from file_processor import *
from utils.exceptions import *

sem = asyncio.Semaphore(8)

entities_count_lock = asyncio.Lock()
total_entities = 0


async def process_one_file(es: AsyncElasticsearch, client: AsyncClient, file_path: str, dataset_name: str):
    global total_entities
    file_entry = File(file_path)
    try:
        print(f"Processing {file_entry}")
        await file_entry.process(client)

        if not file_entry.valid:
            print(f"{Fore.MAGENTA}{file_entry}: could not be processed{Style.RESET_ALL}")
            return

        await index_file(es, dataset_name, file_entry)

        async with entities_count_lock:
            total_entities += len(file_entry.entities)
        print(
            f"{Fore.GREEN}{file_entry}: finished with {len(file_entry.entities)} entities{Style.RESET_ALL}")

    except TikaError as e:
        print(f"{file_entry}: Error while communicating with Tika - {e}", file=sys.stderr)
    except ConnectionError:
        print(f"{file_entry}: Cannot connect to Elasticsearch", file=sys.stderr)
    except (httpx.ReadTimeout, requests.exceptions.ReadTimeout):
        print(f"{file_entry}: Read Timeout", file=sys.stderr)


async def worker(task_queue, es: AsyncElasticsearch, client: AsyncClient, dataset_name: str):
    while True:
        file_path = await task_queue.get()
        if file_path is None:  # Sentinel value to indicate the worker should stop
            break
        try:
            await process_one_file(es, client, file_path, dataset_name)
        except Exception as e:
            print(f"{file_path}: Fatal error - {e}", file=sys.stderr)
        finally:
            task_queue.task_done()


async def run_pipeline(paths: list[str], dataset_name: str):
    try:
        print("Initializing NERvana pipeline...")
        es = get_async_elastic_client()

        # larger files need more time to be processed
        timeout = httpx.Timeout(300)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # dummy request so nametag loads the models
            await initialize_nametag(client)
            print("Testing Elasticsearch connection...")
            await test_connection_async(es)
            print("Checking index in elasticsearch...")
            await assert_index_exists(es, dataset_name)
            print("DONE")
            print("Ready to process files...")

            task_queue = asyncio.Queue()
            num_workers = 4  # Number of worker coroutines

            # Create worker tasks
            workers = [asyncio.create_task(worker(task_queue, es, client, dataset_name)) for _ in range(num_workers)]

            # Add file paths to the task queue
            for file_path in paths:
                await task_queue.put(file_path)

            # Wait for all tasks in the queue to be processed
            await task_queue.join()

            # Stop the worker tasks
            for _ in range(num_workers):
                await task_queue.put(None)
            await asyncio.gather(*workers)

    except ConnectionError:
        print("Cannot connect to Elasticsearch", file=sys.stderr)
        exit(1)
    except AuthenticationException as e:
        print("Cannot authenticate to Elasticsearch:", e, file=sys.stderr)
        exit(1)
    except (FileNotFoundError, JSONDecodeError) as e:
        print("Error while trying to read config file:", e, file=sys.stderr)
        exit(1)
    except httpx.HTTPStatusError as e:
        print("Error while trying to connect to Nametag:", e, file=sys.stderr)
        exit(1)

    finally:
        await es.close()


def get_cl_arguments() -> Tuple[str, str]:
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
    if len(sys.argv) != 3:
        print("Please provide a root directory and a dataset name", file=sys.stderr)
        exit(1)
    load_dotenv()

    root_dir, dataset_name = get_cl_arguments()
    print(f"Looking for files in directory: {root_dir}")
    start_time = time.time()
    try:
        files_paths: list[str] = get_files(root_dir)
    except NotADirectoryError:
        print("Path specified is not a directory:", file=sys.stderr)
        exit(1)

    print(f"Found {len(files_paths)} files")

    asyncio.run(run_pipeline(files_paths, dataset_name))

    duration = time.time() - start_time
    print(
        f"NERvana finished in {duration:.2f} seconds! Total entities indexed: {total_entities}. Average entities per file: {total_entities // len(files_paths)}")
