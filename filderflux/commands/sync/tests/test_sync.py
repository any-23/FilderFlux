import os
import tempfile
import shutil
import pathlib
import signal
import time
import argparse
from threading import Thread
from filderflux.commands.sync.sync import (
    get_all_files,
    get_all_folders,
    remove_redundant_files,
    remove_redundant_folders,
    compare_files,
    copy_folder,
    copy_file,
    sync_folder,
    handle_sync,
    build_path,
)
from filderflux.commands.sync import sync


def test_shutdown_handler():
    """
    Unit test the shutdown_handler function to ensure it sets the shutdown_flag to True.

    This test simulates the behaviour of the shutdown_handler when it receives a SIGINT
    signal. It first resets the shutdown_flag to False, then calls the shutdown_handler,
    and finally asserts that the shutdown_flag has been set to True.

    The shutdown_handler function is expected to set the shutdown_flag to True when it
    handles a SIGINT signal, which is typically sent when a user interrupts the program
    (Ctrl+C).

    Raises:
        AssertionError: If the shutdown_flag is not set to True after calling the
                        shutdown_handler.
    """

    sync.shutdown_flag = False

    sync.shutdown_handler(signal.SIGINT, None)

    assert sync.shutdown_flag, "Expected shutdown flag to be True after calling the shutdown handler."


def create_temporary_folder():
    """
    Create a temporary folder and return its path.

    Returns:
    str: Path to the newly created temporary folder.
    """

    return tempfile.mkdtemp()


def create_temporary_file(folder: str, filename: str, content: str = "Sample content.") -> str:
    """
    Create a temporary file inside the specified folder and return its path.

    Parameters:
    folder (str): The path to the folder where the temporary file will be created.
    filename (str): The name of the temporary file to be created.
    content (str): The content to write to the temporary file. Defaults to "Sample content."

    Returns:
    str: The path to the created temporary file.
    """

    path = os.path.join(folder, filename)
    with open(path, "w") as temp_file:
        temp_file.write(content)
    return path


def create_blank_temporary_file(folder: str, filename: str) -> str:
    """
    Create a blank temporary file inside the specified folder and return its path.

    Parameters:
    folder (str): The path to the folder where the temporary file will be created.
    filename (str): The name of the temporary file to be created.

    Returns:
    str: The path to the created temporary file.
    """

    path = os.path.join(folder, filename)
    with open(path, "w") as _:
        pass
    return path


def test_get_all_folders():
    """
    Test the get_all_folders function to ensure it correctly identifies all subfolders within a specified folder.

    Steps:
    1. Create a temporary test folder.
    2. Create a subfolder within the test folder.
    3. Verify that the subfolder is included in the set of folders returned by get_all_folders.
    4. Clean up by deleting the temporary test folder and its contents.

    Raises:
    AssertionError: If the subfolder is not found in the set of folders returned by get_all_folders.
    """

    test_folder = create_temporary_folder()
    subfolder = os.path.join(test_folder, "subfolder")
    os.makedirs(subfolder)

    folders = get_all_folders(pathlib.Path(test_folder))
    assert pathlib.Path(subfolder) in folders, f"Expected {subfolder} in folders."

    shutil.rmtree(test_folder)


def test_get_all_files():
    """
    Unit test to verify the functionality of get_all_files function.

    Creates a temporary folder with files and subfolders, then checks if
    get_all_files correctly identifies all files within the test folder
    and its subfolders.

    Raises AssertionError if any expected file is missing from the result.
    """

    test_folder = create_temporary_folder()
    test_file = create_temporary_file(test_folder, "file.txt")
    subfolder = os.path.join(test_folder, "subfolder")
    os.makedirs(subfolder)
    subfolder_file = create_temporary_file(subfolder, "subfile.txt")

    files = get_all_files(pathlib.Path(test_folder))
    assert pathlib.Path(test_file) in files, f"Expected {test_file} in files."
    assert pathlib.Path(subfolder_file) in files, f"Expected {subfolder_file} in files."

    shutil.rmtree(test_folder)


def test_remove_redundant_folders():
    """
    Unit test to verify the functionality of remove_redundant_folders function.

    Creates a temporary folder with multiple subfolders, defines a set of folders
    to preserve, and checks if remove_redundant_folders correctly removes folders
    that are not in the set of folders to preserve.

    Raises AssertionError if any unexpected folder remains after calling the function.
    """

    test_folder = create_temporary_folder()
    subfolder1 = os.path.join(test_folder, "subfolder1")
    subfolder2 = os.path.join(test_folder, "subfolder2")
    os.makedirs(subfolder1)
    os.makedirs(subfolder2)

    folders_to_preserve = {pathlib.Path(subfolder1)}

    remove_redundant_folders(pathlib.Path(test_folder), folders_to_preserve)

    remaining_folders = get_all_folders(pathlib.Path(test_folder))
    assert pathlib.Path(subfolder1) in remaining_folders, f"Expected {subfolder1} in remaining folders."
    assert pathlib.Path(subfolder2) not in remaining_folders, f"Expected {subfolder2} to be removed."

    shutil.rmtree(test_folder)


def test_remove_redundant_files():
    """
    Unit test to verify the functionality of remove_redundant_files function.

    Creates a temporary folder with multiple files, defines a set of files
    to preserve, and checks if remove_redundant_files correctly removes files
    that are not in the set of files to preserve.

    Raises AssertionError if any unexpected file remains after calling the function.
    """

    test_folder = create_temporary_folder()
    test_file1 = create_temporary_file(test_folder, "file1.txt")
    test_file2 = create_temporary_file(test_folder, "file2.txt")

    files_to_preserve = {pathlib.Path(test_file1)}

    remove_redundant_files(pathlib.Path(test_folder), files_to_preserve)

    remaining_files = get_all_files(pathlib.Path(test_folder))
    assert pathlib.Path(test_file1) in remaining_files, f"Expected {test_file1} in remaining files."
    assert pathlib.Path(test_file2) not in remaining_files, f"Expected {test_file2} to be removed."

    shutil.rmtree(test_folder)


def test_build_path():
    """
    Unit test for the build_path function.

    - Tests building a path with a basic folder and name.
    - Tests building a path with a nested name.
    - Tests building a path with an empty name.
    - Tests building a path starting from the root.
    - Tests building a path using a relative folder path.
    - Tests building a path with special characters in the name.

    Each test case asserts that the returned path from build_path matches the expected path.
    """

    # basic test case
    folder_path = pathlib.Path("/home/user")
    name = pathlib.Path("documents")
    expected_path = pathlib.Path("/home/user/documents")
    assert build_path(folder_path, name) == expected_path, "Expected path to be '/home/user/documents'"

    # nested name
    name = pathlib.Path("documents/reports")
    expected_path = pathlib.Path("/home/user/documents/reports")
    assert build_path(folder_path, name) == expected_path, "Expected path to be '/home/user/documents/reports'"

    # empty name
    name = pathlib.Path("")
    expected_path = pathlib.Path("/home/user")
    assert build_path(folder_path, name) == expected_path, "Expected path to be '/home/user'"

    # root path
    folder_path = pathlib.Path("/")
    name = pathlib.Path("home/user")
    expected_path = pathlib.Path("/home/user")
    assert build_path(folder_path, name) == expected_path, "Expected path to be '/home/user'"

    # relative folder path
    folder_path = pathlib.Path("home/user")
    name = pathlib.Path("documents")
    expected_path = pathlib.Path("home/user/documents")
    assert build_path(folder_path, name) == expected_path, "Expected path to be 'home/user/documents'"

    # special characters
    folder_path = pathlib.Path("/home/user")
    name = pathlib.Path("docu#ments/repo@rts")
    expected_path = pathlib.Path("/home/user/docu#ments/repo@rts")
    assert build_path(folder_path, name) == expected_path, "Expected path to be '/home/user/docu#ments/repo@rts'"


def test_compare_files():
    """
    Unit test for the compare_files function.

    - Tests comparing two identical files.
    - Tests comparing two files with different content.
    - Tests comparing an existing file with a non-existent file.
    - Tests comparing two non-existent files.
    - Tests comparing two blank files.

    Each test case asserts that the return value from compare_files matches the expected comparison result.
    """

    test_folder = create_temporary_folder()

    file1 = create_temporary_file(test_folder, "file1.txt", "This is some content.")
    file2 = create_temporary_file(test_folder, "file2.txt", "This is some content.")
    file3 = create_temporary_file(test_folder, "file3.txt", "This is some different content.")
    file4 = os.path.join(test_folder, "file4.txt")  # non-existent case
    file5 = create_blank_temporary_file(test_folder, "file5.txt")
    file6 = create_blank_temporary_file(test_folder, "file6.txt")

    # identical files
    assert compare_files(pathlib.Path(file1), pathlib.Path(file2)), "Expected files to be identical."

    # non-identical files
    assert not compare_files(pathlib.Path(file1), pathlib.Path(file3)), "Expected files to be different."

    # existing file vs. non0existing file
    assert not compare_files(
        pathlib.Path(file1), pathlib.Path(file4)
    ), "Expected comparison with non-existent file to be False."

    # non-existing file vs. non-existing file
    assert not compare_files(
        pathlib.Path(file4), pathlib.Path(file4)
    ), "Expected comparison of two non-existent files to be False."

    # test two blank files
    assert compare_files(pathlib.Path(file5), pathlib.Path(file6)), "Expected two blank files to be identical"

    shutil.rmtree(test_folder)


def test_copy_file():
    """
    Unit test for the copy_file function.

    - Tests copying an existing file to a replica file.
    - Tests copying a non-existing file (should not create a replica file).

    Each test case asserts the expected behaviour of the copy_file function.
    """

    # existing file
    test_folder = create_temporary_folder()
    source_file = create_temporary_file(test_folder, "source_file.txt", "This is some content.")
    replica_file = os.path.join(test_folder, "replica_file.txt")

    copy_file(pathlib.Path(source_file), pathlib.Path(replica_file))

    assert os.path.exists(replica_file), "Expected the replica file to exist."
    with open(replica_file, "r") as file:
        assert file.read() == "This is some content.", "Expected the replica file content to match the source file."

    # non-existing file
    non_existing_source = os.path.join(test_folder, "non_existing.txt")
    non_existing_replica = os.path.join(test_folder, "non_existing_replica.txt")

    copy_file(pathlib.Path(non_existing_source), pathlib.Path(non_existing_replica))

    assert not os.path.exists(non_existing_replica), "Expected the replica file not to exist for non-existing source."

    shutil.rmtree(test_folder)


def test_copy_folder():
    """
    Unit test for the copy_folder function.

    - Tests copying an existing source folder to a replica folder.

    Each test case asserts the expected behaviour of the copy_folder function.
    """

    # existing folder
    test_folder = create_temporary_folder()
    source_folder = create_temporary_folder()
    replica_folder = os.path.join(test_folder, "replica_folder")

    copy_folder(pathlib.Path(source_folder), pathlib.Path(replica_folder), pathlib.Path(source_folder).parent)

    assert os.path.exists(replica_folder), "Expected the replica folder to exist after copying."

    shutil.rmtree(test_folder)
    shutil.rmtree(source_folder)


def test_sync_folder():
    """
    Unit test for the sync_folder function.

    - Tests syncing an empty source folder with an empty replica folder.
    - Tests syncing a source folder containing only files.
    - Tests syncing a source folder containing only subfolders.
    - Tests syncing a source folder containing both files and subfolders.
    - Tests syncing a source folder where the replica folder already exists and needs synchronization.

    Each test case asserts the expected behaviour of the sync_folder function.
    """

    # source and replica folders are empty
    source_folder = create_temporary_folder()
    replica_folder = create_temporary_folder()

    sync_folder(pathlib.Path(source_folder), pathlib.Path(replica_folder))

    assert get_all_folders(pathlib.Path(replica_folder)) == set(), "Expected replica folder to remain empty."
    assert get_all_files(pathlib.Path(replica_folder)) == set(), "Expected replica folder to remain empty."

    # source folder contains only files
    source_folder = create_temporary_folder()
    source_file = create_temporary_file(source_folder, "source_file.txt", "This is some content.")
    replica_folder = create_temporary_folder()

    sync_folder(pathlib.Path(source_folder), pathlib.Path(replica_folder))

    assert get_all_folders(pathlib.Path(replica_folder)) == set(), "Expected replica folder to remain empty."
    assert {file.name for file in get_all_files(pathlib.Path(replica_folder))} == {
        os.path.basename(source_file)  # extract last component of the path
    }, "Expected files to be copied."

    # source folder contains only subfolders
    source_folder = create_temporary_folder()
    subfolder = os.path.join(source_folder, "subfolder")
    os.makedirs(subfolder)
    replica_folder = create_temporary_folder()

    sync_folder(pathlib.Path(source_folder), pathlib.Path(replica_folder))

    assert {folder.name for folder in get_all_folders(pathlib.Path(replica_folder))} == {
        os.path.basename(subfolder)
    }, "Expected subfolders to be copied."
    assert get_all_files(pathlib.Path(replica_folder)) == set(), "Expected replica folder to contain only subfolders."

    # source folder contains both files and subfolders
    source_folder = create_temporary_folder()
    source_file = create_temporary_file(source_folder, "source_file.txt", "This is some content.")
    subfolder = os.path.join(source_folder, "subfolder")
    os.makedirs(subfolder)
    replica_folder = create_temporary_folder()

    sync_folder(pathlib.Path(source_folder), pathlib.Path(replica_folder))

    assert {folder.name for folder in get_all_folders(pathlib.Path(replica_folder))} == {
        os.path.basename(subfolder)
    }, "Expected subfolders to be copied."
    assert {file.name for file in get_all_files(pathlib.Path(replica_folder))} == {
        os.path.basename(source_file)
    }, "Expected files to be copied."

    # replica folder already exists and needs to be synchronised with the source folder
    source_folder = create_temporary_folder()
    source_file = create_temporary_file(source_folder, "source_file.txt", "This is some updated content.")
    subfolder = os.path.join(source_folder, "subfolder")
    os.makedirs(subfolder)
    replica_folder = create_temporary_folder()
    replica_subfolder = os.path.join(replica_folder, "subfolder")
    os.makedirs(replica_subfolder)

    sync_folder(pathlib.Path(source_folder), pathlib.Path(replica_folder))

    assert {folder.name for folder in get_all_folders(pathlib.Path(replica_folder))} == {
        os.path.basename(subfolder)
    }, "Expected subfolders to be synchronised."
    assert {file.name for file in get_all_files(pathlib.Path(replica_folder))} == {
        os.path.basename(source_file)
    }, "Expected only the source file to be synchronised."

    shutil.rmtree(replica_folder)
    shutil.rmtree(source_folder)


def test_handle_sync():
    """
    Unit test for the handle_sync function.

    - Tests handling synchronisation when both source and replica folders are initially empty.
    - Tests updating the replica folder when it already exists with pre-existing content.
    - Tests behaviour when the source or the replica folder do not exist.
    - Tests successful completion of synchronisation process with expected file synchronisation.
    - Tests interruption of synchronisation process upon receiving a shutdown signal.

    Each test case verifies the expected behaviour of the handle_sync function based on different scenarios.
    """

    # both source and replica folders are empty
    source_folder = create_temporary_folder()
    replica_folder = create_temporary_folder()

    args = argparse.Namespace(source=source_folder, replica=replica_folder, interval=1)
    handle_sync(args)

    assert get_all_folders(pathlib.Path(replica_folder)) == set(), "Expected replica folder to remain empty."
    assert get_all_files(pathlib.Path(replica_folder)) == set(), "Expected replica folder to remain empty."

    # the replica folder already exists -> update is needed
    source_folder = create_temporary_folder()
    source_file = create_temporary_file(source_folder, "source_file.txt", "This is some updated content.")
    subfolder = os.path.join(source_folder, "subfolder")
    os.makedirs(subfolder)
    replica_folder = create_temporary_folder()
    replica_subfolder = os.path.join(replica_folder, "subfolder")
    os.makedirs(replica_subfolder)

    args = argparse.Namespace(source=source_folder, replica=replica_folder, interval=1)
    handle_sync(args)

    assert {folder.name for folder in get_all_folders(pathlib.Path(replica_folder))} == {
        os.path.basename(subfolder)
    }, "Expected subfolders to be synced."
    assert {file.name for file in get_all_files(pathlib.Path(replica_folder))} == {
        os.path.basename(source_file)
    }, "Expected only the source file to be synced."

    # source or replica folder do not exist
    non_existing_source_folder = "/non_existing_source"
    non_existing_replica_folder = "/non_existing_replica"

    args = argparse.Namespace(source=non_existing_source_folder, replica=non_existing_replica_folder, interval=1)
    handle_sync(args)

    assert not os.path.exists(non_existing_source_folder), "Expected source folder not to be created."
    assert not os.path.exists(non_existing_replica_folder), "Expected replica folder not to be created."

    # the synchronisation process completes successfully
    source_folder = create_temporary_folder()
    source_file = create_temporary_file(source_folder, "source_file.txt", "This is some content.")
    replica_folder = create_temporary_folder()

    args = argparse.Namespace(source=source_folder, replica=replica_folder, interval=1)
    sync_thread = Thread(
        target=handle_sync, args=(args,)
    )  # multiple functions are running concurrently in the same process, using threads is beneficial for testing
    # scenarios where verifying synchronisation, interruption, or completion behaviours without blocking the main thread

    sync_thread.start()

    time.sleep(1)

    assert {file.name for file in get_all_files(pathlib.Path(replica_folder))} == {
        os.path.basename(source_file)
    }, "Expected files to be synchronised."

    sync_thread.join()

    # the shutdown signal interrupts the synchronisation process
    source_folder = create_temporary_folder()
    source_file = create_temporary_file(source_folder, "source_file.txt", "This is some content.")
    replica_folder = create_temporary_folder()

    args = argparse.Namespace(source=source_folder, replica=replica_folder, interval=1)

    sync_thread = Thread(target=handle_sync, args=(args,))
    sync_thread.start()

    time.sleep(1)

    sync.shutdown_flag = True

    sync_thread.join()

    assert not sync_thread.is_alive(), "Expected synchronisation process to be interrupted."

    shutil.rmtree(replica_folder)
    shutil.rmtree(source_folder)
