try:
    from picamera2 import Picamera2
    PICAM_AVAILABLE = True
except ImportError:
    PICAM_AVAILABLE = False
    
import time

class Camera:
    def __init__(self):
        self.picam2 = None
        try:
            if PICAM_AVAILABLE:
                self.picam2 = Picamera2()
                self.picam2.start()
                time.sleep(2)
                print("Camera initialized successfully.")
            else:
                print("Picamera2 library not available. Camera functionality will be disabled.")
        except Exception as e:
            print("Couldn't initialize camera.")
    
    def capture(self, filename=None):
        if PICAM_AVAILABLE:
            if filename is None:
                filename = "/home/admin/Documents/GitHub/edge/app/web/static/image.jpg"
            else:
                filename = f"/home/admin/Documents/GitHub/edge/app/web/static/{filename}"
            self.picam2.capture_file(filename)
            return filename
        else:
            print("Picamera2 not available")
            
    def capture_array(self):
        """Captures an image directly to memory as a numpy array."""
        if PICAM_AVAILABLE:
            return self.picam2.capture_array()
        else:
            print("Picamera2 not available")
            return None

    def close(self):
        if PICAM_AVAILABLE:
            self.picam2.stop()
            print("Camera closed.")
        else:
            print("Picamera2 not available")