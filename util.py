import os
import time


def __console__(color, message):
    NC = "\033[0m"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{timestamp}] {message}{NC}")


def log(m): return __console__("\033[0;32m", m)
def error(m): return __console__("\033[0;31m", m)


def ensureFolder(path):
    if not os.path.exists(path):
        log(f"{path} does not exist, creating")
        os.makedirs(path)


def fetchLocalImages(path, extension=".jpg"):
    log("Fetching local images")

    if not os.path.exists(path):
        error(f"{path} does not exist")
        return []

    dist = os.listdir(path)
    files = [f for f in dist if os.path.isfile(os.path.join(path, f))]
    jpg_files = [f for f in files if f.lower().endswith(extension)]
    full_paths = [os.path.join(path, f) for f in jpg_files]
    sorted_files = sorted(full_paths, key=os.path.getmtime, reverse=True)

    return sorted_files
