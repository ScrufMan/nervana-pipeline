import sys

import tika
from file_processor import *
from entity_recognizer.recognition_manager import find_entities_in_file
from elastic import *


def main():
    tika.initVM()

    files = get_files(sys.argv[1])
    es = get_elastic_client()

    for file_entry in files:
        file_entry.process_file()

        plaintext = file_entry.plaintext

        entities = find_entities_in_file(file_entry)

        # index_data(entities, "test_filesystem", es)

    res = search_by_value("MOPET", "test_filesystem", es)
    res = aggregate_by_field("category", "test_filesystem", es)


if __name__ == '__main__':
    main()
