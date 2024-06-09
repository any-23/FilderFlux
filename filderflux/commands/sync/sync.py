import argparse
import logging
from typing import Set
import pathlib

logger = logging.getLogger(__name__)


def get_all_folders(folder_path: pathlib.Path) -> Set[pathlib.Path]:
    pass


def get_all_files(folder_path: pathlib.Path) -> Set[pathlib.Path]:
    pass


def remove_redundant_folders(folder_path: pathlib.Path, folders_to_preserve: Set[pathlib.Path]) -> None:
    pass


def remove_redundant_files(folder_path: pathlib.Path, files_to_preserve: Set[pathlib.Path]) -> None:
    pass


def build_path(folder_path: pathlib.Path, name: str) -> pathlib.Path:
    pass


def compare_files(file_path_1: pathlib.Path, file_path_2: pathlib.Path) -> bool:
    pass


def copy_file(file_path_1: pathlib.Path, file_path_2: pathlib.Path) -> None:
    pass


def copy_folder(folder_path_1: pathlib.Path, folder_path_2: pathlib.Path) -> None:
    pass


def sync_folder(source_folder_path: pathlib.Path, replica_folder_path: pathlib.Path) -> None:
    """
    base root function - recursive one

    """
    if not source_folder_path.is_dir():
        logger.error(f"{source_folder_path.absolute()} is not folder anymore, cannot be replicated.")
        return  # somebody removed directory during synchronisation

    if not replica_folder_path.exists():
        copy_folder(source_folder_path, replica_folder_path)
        return

    if replica_folder_path.is_file():
        logger.error(f"{replica_folder_path.absolute()} is file now, will be handled in the next iteration.")
        return

    folders = get_all_folders(source_folder_path)
    files = get_all_files(source_folder_path)

    remove_redundant_folders(replica_folder_path, folders)
    remove_redundant_files(replica_folder_path, files)

    for file in files:
        replica_file = build_path(replica_folder_path, file.name)
        equal = compare_files(file, replica_file)
        if not equal:
            copy_file(file, replica_file)

    for folder in folders:
        replica_folder = build_path(replica_folder_path, folder.name)
        sync_folder(folder, replica_folder)


def handle_sync(args: argparse.Namespace) -> None:
    logger.info(
        f"Source folder is {args.source}.  Replica folder is {args.replica}. Interval is set to {args.interval} seconds."
    )
