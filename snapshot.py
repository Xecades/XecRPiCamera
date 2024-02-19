import util
import time
import subprocess
import RPi.GPIO as GPIO
import cvfilter
from props import *


class Snapshot:
    def __init__(self, parent):
        self.lock = False
        self.last = time.time()
        self.pin = SNAPSHOT_PIN
        self.pa = parent

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.RISING,
                              callback=self.take, bouncetime=200)

    def take(self, _):
        if self.last + SNAPSHOT_DT > time.time() or self.lock:
            return

        util.log("Taking snapshot")

        self.pa.cameraView.preview.pause()
        time.sleep(UPDATE_DELAY / 1000)

        method = self.pa.cameraView.filter.method
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file = f"snapshot_{timestamp}.jpg"
        path = f"{DCIM}/{file}"

        cmd = ["raspistill", "-vf", "-hf", "-n",
               "-x", f"IFD0.Make={CAM_NAME}", "-o", path]
        if method == "retro":
            cmd += ["-w", str(RETRO_W), "-h", str(RETRO_H)]

        # ret = subprocess.call(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        # proc = subprocess.run(cmd)

        if proc.returncode == 0:
            util.log(f"Snapshot taken and saved at {path}")

            util.log(f"Processing image with {method}")

            util.processImageCV(path, cvfilter.choose(method))
            if method == "retro":
                util.log(f"Adding timestamp for retro mode")
                util.processImagePIL(path, util.timestamp)

            self.pa.cameraView.button.updateThumbnail(path)
            self.pa.galleryView.refreshList()
            self.pa.cameraView.preview.resume()
        else:
            util.error(f"Failed to take snapshot")
            self.pa.cameraView.preview.resume()

        util.log("Snapshot process complete")

        self.last = time.time()

    def __del__(self):
        GPIO.cleanup()
