try:
    from picamera2 import Picamera2
    PICAM_AVAILABLE = True
except ImportError:
    PICAM_AVAILABLE = False

class Camera:
    def capture(self):
        if PICAM_AVAILABLE:
            filename = "image.jpg"
            picam2 = Picamera2()
            picam2.start()
            picam2.capture_file(filename)
            picam2.stop()
            return filename
        else:
            print("Picamera2 not available")