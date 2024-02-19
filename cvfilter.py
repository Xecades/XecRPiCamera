import cv2
import numpy as np
from scipy.interpolate import UnivariateSpline


def __LookupTable(x, y): return UnivariateSpline(x, y)(range(256))
def __SepiaMat(amount): return np.eye(3) * (1 - amount) + __SEPIA * amount


__SEPIA = np.matrix([[.272, .534, .131],
                     [.349, .686, .168],
                     [.393, .769, .189]])
__SEPIA_DEF = __SepiaMat(.93)
__SW_INC_TABLE = __LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
__SW_DEC_TABLE = __LookupTable([0, 64, 128, 256], [0, 50, 100, 256])


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


def vanilla(img): return img
def greyscale(img): return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def sepia(img):
    ret = np.array(img, dtype=np.float64)
    ret = cv2.transform(ret, __SEPIA_DEF)
    ret[np.where(ret > 255)] = 255
    ret = np.array(ret, dtype=np.uint8)
    return ret


def summer(img):
    B, G, R = cv2.split(img)
    R = cv2.LUT(R, __SW_INC_TABLE).astype(np.uint8)
    B = cv2.LUT(B, __SW_DEC_TABLE).astype(np.uint8)
    return cv2.merge((B, G, R))


def winter(img):
    B, G, R = cv2.split(img)
    R = cv2.LUT(R, __SW_DEC_TABLE).astype(np.uint8)
    B = cv2.LUT(B, __SW_INC_TABLE).astype(np.uint8)
    return cv2.merge((B, G, R))
