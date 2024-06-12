import argparse
import logging
from typing import Set
import pathlib
import shutil
import signal
import time

logger = logging.getLogger(__name__)

shutdown_flag = False


def shutdown_handler(signum, frame):
    global shutdown_flag
    logger.info("Gracefully shutting down...")
    shutdown_flag = True


signal.signal(signal.SIGINT, shutdown_handler)


def get_all_folders(folder_path: pathlib.Path) -> Set[pathlib.Path]:
    """
    Gets all folders within the given folder, recursively.
    """

    folders = set()

    for path in folder_path.rglob("*"):
        if path.is_dir():
            folders.add(path)
    return folders


def get_all_files(folder_path: pathlib.Path) -> Set[pathlib.Path]:
    """
    Gets all folders within the given folder, recursively.
    """

    files = set()

    for path in folder_path.rglob("*"):
        if path.is_file():
            files.add(path)
    return files


def remove_redundant_folders(folder_path: pathlib.Path, folders_to_preserve: Set[pathlib.Path]) -> None:
    """
    Remove folders from the folder_path that are not in folders_to_preserve.
    """
    for path in folder_path.iterdir():
        if path.is_dir() and path not in folders_to_preserve:
            logger.info(f"Removing redundant folder: {path}")
            try:
                shutil.rmtree(path)
            except Exception as e:
                logger.error(f"Error removing folder {path}: {e}")


def remove_redundant_files(folder_path: pathlib.Path, files_to_preserve: Set[pathlib.Path]) -> None:
    """
    Remove files from the folder_path that are not in files_to_preserve.
    """
    for path in folder_path.iterdir():
        if path.is_file() and path not in files_to_preserve:
            logger.info(f"Removing redundant file: {path}")
            try:
                path.unlink()
            except Exception as e:
                logger.error(f"Error removing file {path}: {e}")


def build_path(folder_path: pathlib.Path, name: pathlib.Path) -> pathlib.Path:
    """
    Build a new path by combining a folder path with a name.
    """
    return folder_path / name


def compare_files(file_path_1: pathlib.Path, file_path_2: pathlib.Path) -> bool:
    """
    Compare the contents of two files to determine if they are identical.
    """
    if not file_path_1.exists() or not file_path_2.exists():
        return False

    if file_path_1.stat().st_size != file_path_2.stat().st_size:
        return False

    chunk_size = 8192

    with file_path_1.open("rb") as f1, file_path_2.open("rb") as f2:
        while True:
            chunk1 = f1.read(chunk_size)
            chunk2 = f2.read(chunk_size)
            if chunk1 != chunk2:
                return False
            if not chunk1:
                return True


def copy_file(source_file_path: pathlib.Path, replica_file_path: pathlib.Path) -> None:
    """
    Copy the content of source file to replica file.
    """
    try:
        with source_file_path.open("rb") as src_file, replica_file_path.open("wb") as repl_file:
            chunk_size = 8192
            while True:
                chunk = src_file.read(chunk_size)
                if not chunk:
                    break
                repl_file.write(chunk)
        logger.info(f"Copied file from {source_file_path} to {replica_file_path}")
    except Exception as e:
        logger.error(f"Error copying file from {source_file_path} to {replica_file_path}: {e}")


def copy_folder(
    source_folder_path: pathlib.Path, replica_folder_path: pathlib.Path, root_folder_path: pathlib.Path
) -> None:
    """
    Recursively copy all files and subfolders from the source folder to the replica folder.
    """
    try:
        replica_folder_path.mkdir(parents=True, exist_ok=True)
        for item in source_folder_path.iterdir():
            relative_item_path = item.relative_to(root_folder_path)
            replica_item_path = replica_folder_path / relative_item_path

            if item.is_dir():
                copy_folder(item, replica_item_path, root_folder_path)
            else:
                replica_item_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, replica_item_path)
                logger.info(f"Copied file from {item} to {replica_item_path}")
        logger.info(f"Copied folder from {source_folder_path} to {replica_folder_path}")
    except Exception as e:
        logger.error(f"Error copying folder from {source_folder_path} to {replica_folder_path}: {e}")


def sync_folder(source_folder_path: pathlib.Path, replica_folder_path: pathlib.Path) -> None:
    """
    Recursively synchronising source folder with replica folder.
    """

    if not source_folder_path.is_dir():
        logger.error(f"{source_folder_path.absolute()} is not folder anymore, cannot be replicated.")
        return  # Somebody removed directory during synchronisation

    if not replica_folder_path.exists():
        copy_folder(source_folder_path, replica_folder_path, source_folder_path)
        return

    if replica_folder_path.is_file():
        logger.error(f"{replica_folder_path.absolute()} is file now, will be handled in the next iteration.")
        return

    folders = get_all_folders(source_folder_path)
    files = get_all_files(source_folder_path)

    full_folders_to_preserve = {
        build_path(replica_folder_path, folder.relative_to(source_folder_path)) for folder in folders
    }
    full_files_to_preserve = {build_path(replica_folder_path, file.relative_to(source_folder_path)) for file in files}

    remove_redundant_folders(replica_folder_path, full_folders_to_preserve)
    remove_redundant_files(replica_folder_path, full_files_to_preserve)

    for file in files:
        replica_file = build_path(replica_folder_path, file.relative_to(source_folder_path))
        equal = compare_files(file, replica_file)
        if not equal:
            copy_file(file, replica_file)

    for folder in folders:
        replica_folder = build_path(replica_folder_path, folder.relative_to(source_folder_path))
        sync_folder(folder, replica_folder)


def handle_sync(args: argparse.Namespace) -> None:
    global shutdown_flag

    logger.info(
        f"Source folder - {args.source}. "
        f"Replica folder - {args.replica}. "
        f"Interval between runs - {args.interval} seconds."
    )
    source_folder_path = pathlib.Path(args.source)
    replica_folder_path = pathlib.Path(args.replica)

    if source_folder_path.exists():
        counter = 0

        while not shutdown_flag:
            sync_folder(source_folder_path, replica_folder_path)
            counter += 1
            logger.info(f"Round {counter} of synchronisation.")
            if not shutdown_flag:
                time.sleep(args.interval)

        counter = 0
        sync_folder(source_folder_path, replica_folder_path)
        logger.info("Synchronisation process completed. Shutdown procedure finished.")

    else:
        logger.error(f"{source_folder_path} does not exist. Cannot synchronise.")
        if replica_folder_path.exists():
            shutil.rmtree(replica_folder_path)
            logger.info(f"Replica folder {replica_folder_path} removed.")
