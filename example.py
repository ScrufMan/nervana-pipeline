import sys

import tika
from file_processor import *

def main():
    tika.initVM()

    files = get_files(sys.argv[1])

    for file in files:
        file.process_file(do_filter=True)
        utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
        print(file.plaintext, file=utf8stdout)

if __name__ == '__main__':
    main()