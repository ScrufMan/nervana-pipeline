import sys

import tika
from file_processor import *
from nametag import *

def main():
    tika.initVM()

    files = get_files(sys.argv[1])

    for file_entry in files:
        file_entry.process_file()
        tokenized_data = recognize_data(file_entry.plaintext)
        parse_data(tokenized_data)


if __name__ == '__main__':
    main()