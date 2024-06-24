import argparse
import logging
from typing import Set
import pathlib
import shutil
import signal
import time
from types import FrameType
from typing import Optional

logger = logging.getLogger(__name__)

shutdown_flag = False


def shutdown_handler(signum: int, frame: Optional[FrameType]) -> None:
    """
    Signal handler for graceful shutdown.

    This function is called when a shutdown signal (such as SIGINT) is received.
    It sets a global shutdown flag to True and logs the shutdown event.

    Args:
    signum (int): The signal number.
    frame (Optional[FrameType]): The current stack frame (can be None).
    """

    global shutdown_flag
    logger.info("Gracefully shutting down...")
    shutdown_flag = True


signal.signal(signal.SIGINT, shutdown_handler)


# not distinguishing between hidden and non-hidden folder/file
def get_all_folders(folder_path: pathlib.Path) -> Set[pathlib.Path]:
    """
    Gets all folders within the given root folder, recursively.

    Args:
    folder_path (pathlib.Path): The root folder path from which to retrieve all subfolders.

    Returns:
    Set[pathlib.Path]: A set containing paths to all subfolders found within the root folder.
    """

    folders = set()

    for path in folder_path.rglob("*"):
        if path.is_dir():
            folders.add(path)
    return folders


def get_all_files(folder_path: pathlib.Path) -> Set[pathlib.Path]:
    """
    Gets all files within the given root folder, recursively.

    Args:
    folder_path (pathlib.Path): The root folder path from which to retrieve all files.

    Returns:
    Set[pathlib.Path]: A set containing paths to all files found within the root folder.
    """

    files = set()

    for path in folder_path.rglob("*"):
        if path.is_file():
            files.add(path)
    return files


def remove_redundant_folders(folder_path: pathlib.Path, folders_to_preserve: Set[pathlib.Path]) -> None:
    """
    Remove folders from the folder_path that are not in folders_to_preserve.

    Args:
    folder_path (pathlib.Path): The root folder path from which to remove redundant subfolders.
    folders_to_preserve (Set[pathlib.Path]): A set containing paths to subfolders that should be preserved.

    Returns:
    None
    """

    for path in folder_path.iterdir():
        if path.is_dir() and path not in folders_to_preserve:
            logger.info(f"Removing redundant folder: {path}")
            try:
                # removing the folder and all its contents
                shutil.rmtree(path)
            except Exception as e:
                logger.error(f"Error removing folder {path}: {e}")


def remove_redundant_files(folder_path: pathlib.Path, files_to_preserve: Set[pathlib.Path]) -> None:
    """
    Remove files from the folder_path that are not in files_to_preserve.

    Args:
    folder_path (pathlib.Path): The root folder path from which to remove redundant files.
    files_to_preserve (Set[pathlib.Path]): A set containing paths to files that should be preserved.

    Returns:
    None
    """

    for path in folder_path.iterdir():
        if path.is_file() and path not in files_to_preserve:
            logger.info(f"Removing redundant file: {path}")
            try:
                # deleting the file
                path.unlink()
            except Exception as e:
                logger.error(f"Error removing file {path}: {e}")


def build_path(folder_path: pathlib.Path, name: pathlib.Path) -> pathlib.Path:
    """
    Build a new path by combining a folder path with a name of a new file or folder.

    Args:
    folder_path (pathlib.Path): The base folder path.
    name (pathlib.Path): The name of the new file or folder to be added to the base folder path.

    Returns:
    pathlib.Path: The combined path.
    """

    return folder_path / name  # concatenation


def compare_files(file_path_1: pathlib.Path, file_path_2: pathlib.Path) -> bool:
    """
    Compare the contents of two files to determine if they are identical.

    Args:
    file_path_1 (pathlib.Path): The path to the first file.
    file_path_2 (pathlib.Path): The path to the second file.

    Returns:
    bool: True if the files are identical, False otherwise.
    """

    # checking existance
    if not file_path_1.exists() or not file_path_2.exists():
        return False

    # comparing sizes
    if file_path_1.stat().st_size != file_path_2.stat().st_size:
        return False

    chunk_size = 8192  # 8 KB

    # chcecksums using hash can be used instead of chunks to improve security (e.g. MD5, SHA 160, SHA 256)

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
    Copy the content of the source file to the replica file.

    Args:
    source_file_path (pathlib.Path): The path to the source file that needs to be copied.
    replica_file_path (pathlib.Path): The path to the replica file where the content will be copied.

    Returns:
    None
    """

    try:
        with source_file_path.open("rb") as src_file, replica_file_path.open("wb") as repl_file:
            chunk_size = 8192  # 8 KB for efficacy
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

    Args:
    source_folder_path (pathlib.Path): The path to the source folder that needs to be copied.
    replica_folder_path (pathlib.Path): The path to the destination folder where the content will be copied.
    root_folder_path (pathlib.Path): The root folder path to preserve the relative structure.

    Returns:
    None
    """

    try:
        replica_folder_path.mkdir(parents=True, exist_ok=True)
        for item in source_folder_path.iterdir():
            relative_item_path = item.relative_to(root_folder_path)
            replica_item_path = replica_folder_path / relative_item_path

            if item.is_dir():
                copy_folder(item, replica_item_path, root_folder_path)
            else:  # handling files
                replica_item_path.parent.mkdir(
                    parents=True, exist_ok=True
                )  # ensure parent folders match those in source
                shutil.copy2(item, replica_item_path)  # copy obtains metadata
                logger.info(f"Copied file from {item} to {replica_item_path}")
        logger.info(f"Copied folder from {source_folder_path} to {replica_folder_path}")
    except Exception as e:
        logger.error(f"Error copying folder from {source_folder_path} to {replica_folder_path}: {e}")


def sync_folder(source_folder_path: pathlib.Path, replica_folder_path: pathlib.Path) -> None:
    """
    Recursively synchronise the source folder with the replica folder.

    Args:
    source_folder_path (pathlib.Path): The path to the source folder that needs to be synchronised.
    replica_folder_path (pathlib.Path): The path to the replica folder where the content will be synchronised.

    Returns:
    None

    This function ensures that the contents of the source folder and its subfolders are mirrored in the replica folder.
    It performs the following steps:
    1. Checks if the source folder is still a directory.
    2. If the replica folder does not exist, it copies the entire source folder to the replica folder.
    3. If the replica path is now a file, it logs an error and returns.
    4. Retrieves all folders and files from the source folder.
    5. Builds sets of full paths for folders and files to preserve in the replica folder.
    6. Removes redundant folders and files from the replica folder that are not in the source folder.
    7. Copies files from the source folder to the replica folder if they are different.
    8. Recursively synchronises subfolders.

    Logs appropriate errors if there are issues during the synchronisation process.
    """
    # somebody removed directory during synchronisation
    if not source_folder_path.is_dir():
        logger.error(f"{source_folder_path.absolute()} is not folder anymore, cannot be replicated.")
        return

    # checking if replica_folder already exists
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

    # removing files/folders that are only in replica
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
    """
    Handles the synchronisation process between the source and replica folders at regular intervals.

    Args:
    args (argparse.Namespace): Command-line arguments containing the source folder path, replica folder path,
    and interval between synchronization runs.

    Returns:
    None

    This function continuously synchronises the source folder with the replica folder until a shutdown signal
    is received.
    It performs the following steps:
    1. Logs the initial settings for the source folder, replica folder, and synchronisation interval.
    2. Checks if the source folder exists.
    3. If the source folder exists:
        a. Initialises a counter to track the number of synchronisation rounds.
        b. Enters a loop that runs until the `shutdown_flag` is set.
        c. In each iteration of the loop:
            i. Calls `sync_folder` to synchronise the folders.
            ii. Increments the counter and logs the current round of synchronisation.
            iii. Sleeps for the specified interval if the shutdown flag is not set.
        d. Performs a final synchronisation after the loop exits.
        e. Logs that the synchronisation process is completed.
    4. If the source folder does not exist:
        a. Logs an error message.
        b. Removes the replica folder if it exists and logs its removal.
    """

    global shutdown_flag

    logger.info(
        f"Source folder - {args.source}. "
        f"Replica folder - {args.replica}. "
        f"Interval between runs - {args.interval} seconds."
    )
    source_folder_path = pathlib.Path(args.source)
    replica_folder_path = pathlib.Path(args.replica)

    if source_folder_path.exists():

        # counting rounds of synhronisation
        counter = 0

        while not shutdown_flag:
            sync_folder(source_folder_path, replica_folder_path)
            counter += 1
            logger.info(f"Round {counter} of synchronisation.")
            if not shutdown_flag:
                time.sleep(args.interval)  # setting time interval between rounds of synchronisation

        sync_folder(source_folder_path, replica_folder_path)
        logger.info("Synchronisation process completed. Shutdown procedure finished.")

    else:
        logger.error(f"{source_folder_path} does not exist. Cannot synchronise.")
        if replica_folder_path.exists():
            shutil.rmtree(replica_folder_path)
            logger.info(f"Replica folder {replica_folder_path} removed.")
