import os

from pyunpack import Archive

archives_suffixes = (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".lzma", ".z", ".Z", ".lz")


def extract_file(file_path: str, extract_to: str):
    try:
        Archive(file_path).extractall(extract_to)
        print(f"Extracted {file_path}")
    except Exception:
        print(f"Could not extract {file_path}")


def get_files(root_dir: str) -> list[str]:
    """
    Returns all absolute file paths reachable from given root directory
    :param root_dir: relative or absolute path
    :return: list of paths
    """
    if not os.path.isdir(root_dir):
        raise NotADirectoryError()

    files_to_process = []

    # absolute path of current working directory
    wd_abs = os.getcwd()

    # path to extract archives to
    extract_dir_name = "extracted"
    while os.path.exists(extract_dir := os.path.join(wd_abs, root_dir, extract_dir_name)):
        extract_dir_name += "_"  # append _ to dir name until it doesn't exist

    # make dir for extracted files
    os.mkdir(extract_dir)

    # TODO: add support for archives in archives
    # find archives and extract them
    for root_current, _, files in os.walk(root_dir):
        for filename in files:
            file_abs_path = os.path.join(wd_abs, root_current, filename)
            if filename.lower().endswith(archives_suffixes):
                extract_file(file_abs_path, extract_dir)

    for root_current, _, files in os.walk(root_dir):
        for filename in files:
            # skip archives, they can overwhelm tika
            if filename.lower().endswith(archives_suffixes):
                continue
            file_abs_path = os.path.join(wd_abs, root_current, filename)
            files_to_process.append(file_abs_path)

    return files_to_process
