import os

MARGIN = 10
SCREEN_W = 480
SCREEN_H = 320
UPDATE_DELAY = 30
IP_DELAY = 1000
DISPLAY_W = 480
DISPLAY_H = 320
G_INFO_H = 50
G_META_H = 25
G_MARGIN = 8
G_PREVIEW_H = SCREEN_H - G_INFO_H - G_META_H
G_PREVIEW_W = int(G_PREVIEW_H * 4 / 3)
DCIM = os.path.expanduser("~/DCIM")
PORT = 80
SNAPSHOT_PIN = 26
SNAPSHOT_DT = 1
CAM_NAME = "LYY&HZ Camera"
BG_COLOR = "#000"
BORDER_COLOR = "#444"
BUTTON_COLOR = "#222"
INFO_COLOR = "#222"
BUTTON_ACTIVE_COLOR = "#1a1a1a"
BUTTON_WARN_COLOR = "#cc1504"
TEXT_COLOR = "#fff"
