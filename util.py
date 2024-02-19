import os
import cv2
import time
import socket
import numpy as np
from PyQt5.QtGui import QImage
from PIL import Image


def __console__(color, message):
    NC = "\033[0m"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{timestamp}] {message}{NC}")


def log(m): return __console__("\033[0;32m", m)
def error(m): return __console__("\033[0;31m", m)


def pil2cv(pil): return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
def cv2pil(cv): return Image.fromarray(cv2.cvtColor(cv, cv2.COLOR_BGR2RGB))


def cv2qt(cv):
    fmt = QImage.Format_RGB888
    if len(cv.shape) == 2:
        fmt = QImage.Format_Grayscale8
    return QImage(cv.data, cv.shape[1], cv.shape[0], fmt)


def both(f1, f2):
    def wrapper():
        f1()
        f2()
    return wrapper


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


def processImage(path, fn):
    pil = Image.open(path)
    exif = pil.getexif()

    img = pil2cv(pil)
    img = fn(img)
    pil = cv2pil(img)

    pil.save(path, exif=exif)


def ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = None
    return ip
