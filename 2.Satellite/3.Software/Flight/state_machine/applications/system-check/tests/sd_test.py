import os
from lib.pycubed import cubesat


def sd_test():
    """
    Run a basic test; Create a file and test existence, write to and
    read from a file, delete file and test existence. Return result_dict
    values accordingly
    """

    # create filepaths
    filepath = "test.txt"
    filepath_directory = "/sd/test.txt"

    # try to create a file with the test filepath
    try:
        test_file = open(filepath_directory, "x")
    except OSError:
        # if the file already exists, remove it and create a new file
        os.remove(filepath_directory)
        test_file = open(filepath_directory, "x")

    print(f"Directory after test.txt was created:\n{os.listdir('/sd/')}")
    if filepath not in os.listdir("/sd/"):
        return ("File creation failed.", False)

    # write to file
    test_string = "Hello World! This is a test file.\n"
    try:
        test_file.write(test_string)
    except OSError as e:
        print(f"Unable to write to file. {e}")
        return (f"Unable to write to file. {e}", False)
    test_file.close()

    # read from file
    try:
        test_file_read = open(filepath_directory, "r")
        test_string_read = test_file_read.read()
    except OSError as e:
        print(f"Unable to read from file. {e}")
        return (f"Unable to read from file. {e}", False)

    if test_string_read != test_string:
        print("File not written to or read from correctly.")
        return ("File not written to or read from correctly.", False)

    # delete file
    os.remove(filepath_directory)
    print(f"Directory after test.txt was removed:\n{os.listdir('/sd/')}")

    if filepath in os.listdir("/sd/"):
        return ("File deletion failed.", False)

    # if nothing has failed so far, return success
    return ("""SD Card passed all tests: New file was created, wrote to,
read from, and deleted successfully.""", True)


async def run(result_dict):
    """
    Check SD card
    If initialized correctly, run test and update result dictionary
    through sd_test
    If not initialized, update result dictionary
    """

    if cubesat.sdcard:
        print("Starting Basic SD Card test...")
        result_dict["Basic_SDCard_Test"] = sd_test()
        print("Basic SD Card test complete.\n")
    else:
        result_dict["Basic_SDCard_Test"] = (
            "Cannot test logging; no SD Card detected", None)
