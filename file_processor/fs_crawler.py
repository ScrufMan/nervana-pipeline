import os
from typing import List

from .file import File


def get_files(root_dir: str) -> List[File]:
    """
    Finds all files from given root directory
    :param root_dir: relative or absolute path
    :return: List of type File
    """
    all_files = []

    if not os.path.isdir(root_dir):
        print(f"{root_dir} is not a directory")
        return all_files

    wd = os.getcwd()

    for root, subdirs, files in os.walk(root_dir):
        for file in files:
            path = fr"{wd}/{root}/{file}"  # create absolute path
            file_obj = File(path)
            all_files.append(file_obj)

    return all_files
