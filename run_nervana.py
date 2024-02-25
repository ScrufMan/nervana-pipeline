import asyncio
import os
import sys
import time
from json import JSONDecodeError
from typing import Tuple

import httpx
import requests
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import AuthenticationException
from httpx import AsyncClient
from neo4j import AsyncGraphDatabase, AsyncDriver

from config import config
from elastic import (
    get_async_elastic_client,
    test_connection_async,
    assert_index_exists,
    index_file,
)
from file_processor import *
from utils import setup_logger
from utils.exceptions import *

entities_count_lock = asyncio.Lock()
total_entities = 0
logger = setup_logger(__name__)


async def process_one_file(
        es: AsyncElasticsearch,
        client: AsyncClient,
        neo4j_driver: AsyncDriver,
        file: File,
        dataset_name: str,
):
    global total_entities
    try:
        logger.info(f"Processing {file}")
        await file.process(client, neo4j_driver)

        if not file.valid:
            logger.error(f"{file}: could not be processed!")
            return

        await index_file(es, dataset_name, file)

        async with entities_count_lock:
            total_entities += len(file.entities)
        logger.info(f"{file}: finished with {len(file.entities)} entities!")

    except TikaError as e:
        logger.error(f"{file}: Error while communicating with Tika - {e}")
    except ConnectionError:
        logger.error(f"{file}: Cannot connect to Elasticsearch")
    except (httpx.ReadTimeout, requests.exceptions.ReadTimeout):
        logger.error(f"{file}: Read Timeout")


async def worker(
        task_queue,
        es: AsyncElasticsearch,
        client: AsyncClient,
        neo4j_driver: AsyncDriver,
        dataset_name: str,
):
    while True:
        try:
            file: File = await task_queue.get()
            await process_one_file(es, client, neo4j_driver, file, dataset_name)
        except Exception as e:
            logger.error(f"{file}: Fatal error - {e}")
        finally:
            task_queue.task_done()


async def run_pipeline(files: list[File], dataset_name: str):
    try:
        # index name must be lowercase
        dataset_name = dataset_name.lower()
        logger.info("Initializing NERvana pipeline...")
        es = get_async_elastic_client()

        # larger files need more time to be processed
        timeout = httpx.Timeout(300)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # dummy request so nametag loads the models
            logger.info("Initializing Nametag...")
            await initialize_nametag(client)
            neo4j_driver = await initialize_neo4j()
            logger.info("Testing Neo4j connection...")
            await test_neo4j_connection(neo4j_driver)
            logger.info("Testing Elasticsearch connection...")
            await test_connection_async(es)
            logger.info("Checking index in elasticsearch...")
            await assert_index_exists(es, dataset_name)
            logger.info("DONE")
            logger.info("Ready to process files...")

            task_queue = asyncio.Queue()
            # Add files to the task queue
            for file in files:
                task_queue.put_nowait(file)

            n_workers = config.NUM_WORKERS  # Number of worker coroutines
            # Create workers
            tasks = [
                asyncio.create_task(
                    worker(task_queue, es, client, neo4j_driver, dataset_name)
                )
                for _ in range(n_workers)
            ]

            # Wait for all tasks in the queue to be processed
            await task_queue.join()

            # Cancel our worker tasks.
            for task in tasks:
                task.cancel()
            # Wait until all worker tasks are cancelled.
            await asyncio.gather(*tasks, return_exceptions=True)

    except EnvironmentError as e:
        logger.error("Error while trying to read environment variables:", e)
        exit(1)
    except ConnectionError:
        logger.error("Cannot connect to Elasticsearch")
        exit(1)
    except AuthenticationException as e:
        logger.error("Cannot authenticate to Elasticsearch:", e)
        exit(1)
    except (FileNotFoundError, JSONDecodeError) as e:
        logger.error("Error while trying to read config file:", e)
        exit(1)
    except httpx.HTTPStatusError as e:
        logger.error("Error while trying to connect to Nametag:", e)
        exit(1)

    finally:
        if es:
            await es.close()
        if neo4j_driver:
            await neo4j_driver.close()


def get_cl_arguments() -> Tuple[str, str]:
    return sys.argv[1], sys.argv[2]


async def initialize_nametag(client: AsyncClient):
    # get base url from .env
    base_url = os.environ.get("NAMETAG_URL")
    if base_url is None:
        raise EnvironmentError("NAMETAG_URL must be set in .env file")
    url = f"{base_url}/recognize"
    payload = {"data": "initialize"}
    response = await client.post(url, data=payload)
    response.raise_for_status()


async def initialize_neo4j() -> AsyncDriver:
    neo4j_url = os.environ.get("NEO4J_URL")
    neo4j_user = os.environ.get("NEO4J_USER")
    neo4j_password = os.environ.get("NEO4J_PASSWORD")
    if neo4j_url is None or neo4j_user is None or neo4j_password is None:
        raise EnvironmentError(
            "NEO4J_URL, NEO4J_USER and NEO4J_PASSWORD must be set in .env file"
        )
    driver = AsyncGraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))
    return driver


async def test_neo4j_connection(driver: AsyncDriver):
    try:
        async with driver.session() as session:
            await session.run("RETURN 1")
    except Exception as e:
        logger.error("Error while trying to connect to Neo4j:", e)
        exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Please provide a root directory and a dataset name", file=sys.stderr)
        exit(1)
    load_dotenv()

    data_dir, dataset_name = get_cl_arguments()
    root_dir = os.path.join("/nervana_data", data_dir)
    logger.info(f"Looking for files in directory: {root_dir}")
    start_time = time.time()
    try:
        files: list[File] = get_files(root_dir)
    except NotADirectoryError:
        print("Path specified is not a directory:", file=sys.stderr)
        exit(1)

    logger.info(f"Found {len(files)} files")

    asyncio.run(run_pipeline(files, dataset_name))

    duration = time.time() - start_time
    logger.info(
        f"NERvana finished in {duration:.2f} seconds! Number of entities indexed: {total_entities}"
    )
