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
        file_entities = find_entities_in_plaintext(file_entry.plaintext, file_entry.lang, file_id)
        index_entities(es, DATASET, file_entities)
        print(f"File {file_path} done!")

    except TikaError as e:
        print(f"File {file_path}, Error from Tika:", e)
    except NoFileContentError:
        print(f"File {file_path} has no content")
    except Exception as e:
        print(f"Error while processing file {file_path}:", e)


def main():
    files = get_files(sys.argv[1])

    es = get_elastic_client()

    if not test_connection(es):
        print("Cannot connect to Elasticsearch")
        return False

    create_index_if_not_exists(es, DATASET)

    ncpu = os.cpu_count()

    # with ProcessPoolExecutor(max_workers=ncpu) as executor:
    #     for file_path in executor.map(process_one_file, files):
    #         print(f"File {file_path} done!")

    for file_path in files:
        process_one_file(file_path)

    return True


if __name__ == '__main__':
    main()
