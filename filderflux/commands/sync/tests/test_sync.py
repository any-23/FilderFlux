import os
import tempfile
import shutil
import pathlib
import unittest
from filderflux.commands.sync.sync import *


def create_temporary_folder() -> str:
    """
    Create a temporary folder and return its path.
    """
    return tempfile.mkdtemp()


def create_temporary_file(folder_path: str, file_name: str) -> str:
    """
    Create a temporary file inside the specified folder and return its path.
    """
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w") as f:
        f.write("This is test file.")
    return file_path


def test_get_all_folders():
    test_folder = create_temporary_folder()
    subfolder = os.path.join(test_folder, "subfolder")
    os.makedirs(subfolder)

    folders = get_all_folders(pathlib.Path(test_folder))
    assert test_folder in folders
    assert subfolder in folders

    shutil.rmtree(test_folder)


def test_get_all_files():
    test_folder = create_temporary_folder()
    test_file = create_temporary_file(test_folder, "test_file.txt")

    files = get_all_files(pathlib.Path(test_folder))
    assert test_file in files

    shutil.rmtree(test_folder)


def test_remove_redundant_folders():
    # Write your test cases here for remove_redundant_folders function
    pass


def test_remove_redundant_files():
    # Write your test cases here for remove_redundant_files function
    pass


def test_build_path():
    # Write your test cases here for build_path function
    pass


def test_compare_files():
    # Write your test cases here for compare_files function
    pass


def test_copy_file():
    # Write your test cases here for copy_file function
    pass


def test_copy_folder():
    # Write your test cases here for copy_folder function
    pass


def test_sync_folder():
    # Write your test cases here for sync_folder function
    pass


def test_handle_sync():
    # Write your test cases here for handle_sync function
    pass


if __name__ == "__main__":
    test_get_all_folders()
    test_get_all_files()
