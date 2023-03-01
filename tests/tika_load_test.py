import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import tika
from tika import parser


def test_tika_load(path):
    path = path.__str__()
    return parser.from_file(path)


if __name__ == '__main__':
    tika.initVM()
    filepath = Path("sample_files/large_pdf.pdf")
    data = [filepath] * 200

    ncpu = os.cpu_count()

    with ProcessPoolExecutor(max_workers=ncpu) as executor:
        for idx, res in enumerate(executor.map(test_tika_load, data)):
            print(idx)
