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
    sync.shutdown_flag = False

    sync.shutdown_handler(signal.SIGINT, None)

    assert sync.shutdown_flag, "Expected shutdown flag to be True after calling the shutdown handler."


def create_temporary_folder() -> str:
    """
    Create a temporary folder and return its path.
    """
    return tempfile.mkdtemp()


def create_temporary_file(folder, filename, content="Sample content."):
    """
    Create a temporary file inside the specified folder and return its path.
    """
    path = os.path.join(folder, filename)
    with open(path, "w") as temp_file:
        temp_file.write(content)
    return path


def create_blank_temporary_file(folder, filename):
    path = os.path.join(folder, filename)
    with open(path, "w") as _:
        pass
    return path


def test_get_all_folders():
    test_folder = create_temporary_folder()
    subfolder = os.path.join(test_folder, "subfolder")
    os.makedirs(subfolder)

    folders = get_all_folders(pathlib.Path(test_folder))
    assert pathlib.Path(subfolder) in folders, f"Expected {subfolder} in folders."

    shutil.rmtree(test_folder)


def test_get_all_files():
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
    test_folder = create_temporary_folder()
    source_folder = create_temporary_folder()
    replica_folder = os.path.join(test_folder, "replica_folder")

    copy_folder(pathlib.Path(source_folder), pathlib.Path(replica_folder), pathlib.Path(source_folder).parent)

    assert os.path.exists(replica_folder), "Expected the replica folder to exist after copying."


def test_sync_folder():
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
        os.path.basename(source_file)
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


def test_handle_sync():
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

    # the source or replica folders do not exist
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
    sync_thread = Thread(target=handle_sync, args=(args,))
    sync_thread.start()

    time.sleep(1)

    assert {file.name for file in get_all_files(pathlib.Path(replica_folder))} == {
        os.path.basename(source_file)
    }, "Expected files to be synchronised."

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
