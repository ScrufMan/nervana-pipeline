import os

from pyunpack import Archive

from config import config
from utils import setup_logger
from .file import File
from .metadata import get_file_format_magic, extension_from_mime

# suffixes of archives that can be extracted
archives_suffixes = (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".lzma", ".z", ".Z", ".lz")

logger = setup_logger(__name__)


def extract_archive(archive_path: str, extract_dir: str):
    Archive(archive_path).extractall(extract_dir)


def get_files(root_dir: str) -> list[File]:
    """
    Returns all absolute file paths reachable from given root directory
    :param root_dir: relative or absolute path
    :return: list of paths
    """
    if not os.path.isdir(root_dir):
        raise NotADirectoryError()

    all_files: list[File] = []
    # images need to be processed last because OCR is expensive
    files_ocr: list[File] = []

    # absolute path of current working directory
    wd_abs = os.getcwd()

    # directory to extract archives to
    extract_dir_name = "_extracted_by_NERvana"
    extract_dir = os.path.join(wd_abs, root_dir, extract_dir_name)
    if not os.path.exists(extract_dir):
        os.mkdir(extract_dir)

    # TODO: do subsequent checks only in the extract dir
    # iteratively look for archives and extract them until there are no more archives
    while True:
        found_archive = False
        for root_current, _, files in os.walk(root_dir):
            for filename in files:
                file_abs_path = os.path.join(wd_abs, root_current, filename)
                magic_mimetype = get_file_format_magic(file_abs_path)
                suffix = extension_from_mime(magic_mimetype)

                if suffix in archives_suffixes:
                    try:
                        extract_archive(file_abs_path, extract_dir)
                        logger.info(f"Extracted {file_abs_path}")
                        # remove archive after extraction
                        os.remove(file_abs_path)
                    except Exception as e:
                        logger.error(f"Could not extract {file_abs_path}: {e}")

                    found_archive = True
        if not found_archive:
            break

    for root_current, _, files in os.walk(root_dir):
        for filename in files:
            file_abs_path = os.path.join(wd_abs, root_current, filename)
            magic_mimetype = get_file_format_magic(file_abs_path)
            suffix = extension_from_mime(magic_mimetype)

            # files without suffix can be detected by Tika, but unsupported formats are skipped
            if not suffix:
                logger.warning(f"{file_abs_path} - unknown file format")
            elif suffix not in config.SUPPORTED_FORMATS:
                logger.warning(f"{file_abs_path} skipped - unsupported file format: {suffix}")
                continue

            file = File(file_abs_path, suffix)
            if suffix in config.OCR_SUFFIXES:
                files_ocr.append(file)
            else:
                all_files.append(file)

    # add files that need OCR to the end of the list
    all_files.extend(files_ocr)
    return all_files
