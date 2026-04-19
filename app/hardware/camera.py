try:
    from picamera2 import Picamera2
    PICAM_AVAILABLE = True
except ImportError:
    PICAM_AVAILABLE = False
    
import time

class Camera:
    def __init__(self):
        self.picam2 = None
        if PICAM_AVAILABLE:
            self.picam2 = Picamera2()
            self.picam2.start()
            time.sleep(2)
            print("Camera initialized successfully.")
        else:
            print("Camera not available.")
    
    def capture(self):
        if PICAM_AVAILABLE:
            filename = "/home/admin/Documents/GitHub/edge/app/web/static/image.jpg"
            self.picam2.capture_file(filename)
            return filename
        else:
            print("Picamera2 not available")
            
    def close(self):
        if PICAM_AVAILABLE:
            self.picam2.stop()
            print("Camera closed.")
        else:
            print("Picamera2 not available")