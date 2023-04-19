import os
from typing import List


def get_files(root_dir: str) -> List[str]:
    """
    Returns all absolute file paths reachable from given root directory
    :param root_dir: relative or absolute path
    :return: List of type File
    """
    all_files = []

    # Check if root_dir is a directory
    if not os.path.isdir(root_dir):
        raise NotADirectoryError(f"{root_dir} is not a directory")

    # absolute path of current working directory
    wd_abs = os.getcwd()

    for root_current, _, files in os.walk(root_dir):
        for filename in files:
            file_abs_path: str = os.path.join(wd_abs, root_current, filename)
            all_files.append(file_abs_path)

    return all_files
