import sys

import tika
from file_processor import *

def main():
    tika.initVM()

    files = get_files(sys.argv[1])

    for file_entry in files:
        file_entry.process_file()
        print(file_entry.plaintext)

if __name__ == '__main__':
    main()