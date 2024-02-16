import os
from pidng.core import RPICAM2DNG

MARGIN = 5
SCREEN_W = 480
SCREEN_H = 320
UPDATE_DELAY = 70
DISPLAY_W = 160
DISPLAY_H = 120
G_PREVIEW_H = 247
G_PREVIEW_W = int(G_PREVIEW_H * 4 / 3)
DCIM = os.path.expanduser("~/DCIM")
DNG = RPICAM2DNG()
CAM_NAME = "LYY & HZ Camera"
BG_COLOR = "#000"
BORDER_COLOR = "#4d4d4d"
BUTTON_COLOR = "#222"
LABEL_COLOR = "#222"
BUTTON_ACTIVE_COLOR = "#1a1a1a"
BUTTON_WARN_COLOR = "#cc1504"
TEXT_COLOR = "#fff"
