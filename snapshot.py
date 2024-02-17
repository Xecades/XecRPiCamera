import util
import time
import subprocess
import RPi.GPIO as GPIO
from props import *


class Snapshot:
    def __init__(self, parent):
        self.lock = False
        self.pin = SNAPSHOT_PIN
        self.pa = parent

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.FALLING,
                              callback=self.take, bouncetime=200)

    def take(self, _):
        if self.lock:
            return
        self.lock = True

        util.log("Taking snapshot")

        self.pa.cameraView.preview.pause()

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file = f"snapshot_{timestamp}.jpg"
        path = f"{DCIM}/{file}"

        cmd = ["raspistill", "-vf", "-hf", "-n",
               "-x", f"IFD0.Make={CAM_NAME}", "-o", path]
        ret = subprocess.call(cmd)

        if ret == 0:
            util.log(f"Snapshot taken and saved at {path}")

            self.pa.cameraView.button.updateThumbnail(path)
            self.pa.galleryView.refreshList()
            self.pa.galleryView.update()
            self.pa.cameraView.preview.resume()
        else:
            util.error(f"Failed to take snapshot")
            self.pa.cameraView.preview.resume()

        self.lock = False

    def __del__(self):
        GPIO.cleanup()
