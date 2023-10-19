import os

DIRECTORY_STAT = 16384  # the stat value for a directory


def mkdirp(path):
    """Create a directory and all parent directories if necessary."""
    path = path.split('/')
    path = [p for p in path if p != '']
    sd = False
    if path[0] == 'sd':
        path = path[1:]
        sd = True

    for i in range(len(path)):
        subpath = '/'.join(path[:i + 1])
        if sd:
            subpath = '/sd/' + subpath

        try:
            os.mkdir(subpath)
        except Exception:
            pass

def is_dir(path):
    """returns True if item at `path` is a directory, otherwise returns False"""
    stat = os.stat(path)
    if stat[0] == DIRECTORY_STAT:
        return True
    else:
        return False


def joinpath(path1, path2):
    """join path1 and path2 with the os specific separator"""
    return f"{path1}{os.sep}{path2}"


def rmrecursive(path, verbose=False):
    """
    Simple rm -r implementation.
    Recursively deletes everything at path and below
    """
    if is_dir(path):
        for item in os.listdir(path):
            item_path = joinpath(path, item)
            rmrecursive(item_path, verbose=verbose)
        os.rmdir(path)
    else:
        os.remove(path)

    if verbose:
        print(f"Removed {path}")

def filesystem_availability(fs_path):
    """
    return the fraction available of the filesystem at fs_path
    """

    fs_storage_stats = os.statvfs(fs_path)
    fs_storage_avail = fs_storage_stats[3]
    fs_storage_total = fs_storage_stats[2]
    fs_avail = fs_storage_avail / fs_storage_total

    return fs_avail
