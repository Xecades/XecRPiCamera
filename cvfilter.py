import cv2
import numpy as np
from scipy.interpolate import UnivariateSpline


def choose(method):
    fn = vanilla
    if method == "greyscale":
        fn = greyscale
    elif method == "sepia":
        fn = sepia
    elif method == "summer":
        fn = summer
    elif method == "winter":
        fn = winter
    return fn


def LookupTable(x, y):
    spline = UnivariateSpline(x, y)
    return spline(range(256))


def vanilla(img):
    return img


def greyscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def sepia(img):
    SEPIA_MAT = np.matrix([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
    ret = np.array(img, dtype=np.float64)
    ret = cv2.transform(ret, SEPIA_MAT)
    ret[np.where(ret > 255)] = 255
    ret = np.array(ret, dtype=np.uint8)
    return ret


def summer(img):
    incTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    B, G, R = cv2.split(img)
    R = cv2.LUT(R, incTable).astype(np.uint8)
    B = cv2.LUT(B, decTable).astype(np.uint8)
    return cv2.merge((B, G, R))


def winter(img):
    incTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    B, G, R = cv2.split(img)
    R = cv2.LUT(R, decTable).astype(np.uint8)
    B = cv2.LUT(B, incTable).astype(np.uint8)
    return cv2.merge((B, G, R))
