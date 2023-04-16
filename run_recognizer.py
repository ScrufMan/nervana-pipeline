import os
import sys

from file_processor import *
from entity_recognizer.recognition_manager import find_entities_in_plaintext
from elastic import get_elastic_client, test_connection, create_index_if_not_exists, index_file, index_entities
from concurrent.futures import ProcessPoolExecutor

from file_processor.exceptions import *

DATASET = "zachyt_1"


def process_one_file(file_path):
    es = get_elastic_client()
    file_entry = File(file_path)

    try:
        file_entry.process_file()
        file_id = index_file(es, DATASET, file_entry)
        file_entities = find_entities_in_plaintext(file_entry.plaintext, file_entry.language, file_id)
        index_entities(es, DATASET, file_entities)
        print(f"File {file_path} done!")

    except TikaError as e:
        print(f"File {file_path}, Error from Tika:", e)
    except NoFileContentError:
        print(f"File {file_path} has no content")
    except ConnectionError:
        print(f"Cannot connect to Elasticsearch")
    except Exception as e:
        print(f"Error while processing file {file_path}:", e)


def main():
    try:
        files = get_files(sys.argv[1])
    except IndexError:
        print("Please provide a root directory")
        exit(1)
    except NotADirectoryError as e:
        print(e)
        exit(1)
    except Exception as e:
        print("Error while getting files:", e)
        exit(1)

    try:
        es = get_elastic_client()
        test_connection(es)
        create_index_if_not_exists(es, DATASET)
    except ConnectionError:
        print("Cannot connect to Elasticsearch")
        exit(1)
    except Exception as e:
        print("Error while creating index:", e)
        exit(1)

    ncpu = os.cpu_count()

    # with ProcessPoolExecutor(max_workers=ncpu) as executor:
    #     for file_path in executor.map(process_one_file, files):
    #         print(f"File {file_path} done!")

    for file_path in files:
        process_one_file(file_path)

    return 0


if __name__ == '__main__':
    main()
