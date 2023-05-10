import asyncio
import sys
from json import JSONDecodeError
from typing import List, Tuple

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ElasticsearchException

from elastic import (
    get_async_elastic_client,
    test_connection,
    assert_index_exists,
    index_file,
    index_entities,
)
from entity_recognizer.recognition_manager import find_entities_in_plaintext
from file_processor import *
from file_processor.exceptions import *


async def process_one_file(es: AsyncElasticsearch, file_path: str, dataset: str):
    file_entry = File(file_path)

    try:
        await file_entry.process()
        file_id: str = await index_file(es, dataset, file_entry)
        file_entities = find_entities_in_plaintext(
            file_entry.plaintext, file_entry.language, file_id
        )
        await index_entities(es, dataset, file_entities)
        print(f"Processed file {file_path}")

    except TikaError as e:
        print(f"File {file_path}, Error from Tika:", e)
    except NoFileContentError:
        print(f"File {file_path} has no content")
    except ConnectionError:
        print(f"File {file_path}, Cannot connect to Elasticsearch")
    except ElasticsearchException as e:
        print(f"File {file_path}, Elasticsearch error:", e)
    except Exception as e:
        print(f"File {file_path}, Unknown error:", e)


async def run_pipeline(paths: List[str], dataset: str):
    es = get_async_elastic_client()
    try:
        await test_connection(es)
        await assert_index_exists(es, dataset)

        tasks = [process_one_file(es, file_path, dataset) for file_path in paths]
        await asyncio.gather(*tasks)

    except ConnectionError:
        print("Cannot connect to Elasticsearch")
        exit(1)
    except ElasticsearchException as e:
        print("Elasticsearch error:", e)
        exit(1)
    except (FileNotFoundError, JSONDecodeError) as e:
        print("Error while trying to read config file:", e)
        exit(1)
    except Exception as e:
        print("Unknown error in pipeline:", e)
        exit(1)

    finally:
        await es.close()


def get_cl_arguments() -> Tuple[str, str]:
    if len(sys.argv) != 3:
        print("Please provide a root directory and a dataset name")
        exit(1)

    return sys.argv[1], sys.argv[2]


if __name__ == "__main__":
    root_dir, dataset_name = get_cl_arguments()

    try:
        file_paths: List[str] = get_files(root_dir)
    except NotADirectoryError as e:
        print(e)
        exit(1)
    except Exception as e:
        print("Unknown error while getting file paths:", e)
        exit(1)

    asyncio.run(run_pipeline(file_paths, dataset_name))
    print("NERvana finished successfully!")
