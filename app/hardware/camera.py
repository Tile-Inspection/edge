try:
    from picamera2 import Picamera2
    PICAM_AVAILABLE = True
except ImportError:
    PICAM_AVAILABLE = False
    
import time
import cv2

class Camera:
    def __init__(self):
        self.picam2 = None
        self.is_recording = False
        self.video_writer = None
        try:
            if PICAM_AVAILABLE:
                self.picam2 = Picamera2()
                config = self.picam2.create_still_configuration()
                self.picam2.configure(config)
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
            
    def start_recording(self, filename=None):
        if filename is None:
            filename = "/home/admin/Documents/GitHub/edge/app/web/static/video.avi"
        else:
            filename = f"/home/admin/Documents/GitHub/edge/app/web/static/{filename}"
        
        self.is_recording = True
        self.video_writer = None
        self.video_filename = filename
        print(f"Started recording video to {filename}")

    def stop_recording(self):
        self.is_recording = False
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        print("Stopped video recording.")
            
    def capture_array(self):
        """Captures an image directly to memory as a numpy array."""
        if PICAM_AVAILABLE:
            frame = self.picam2.capture_array()
            
            if self.is_recording and frame is not None:
                if self.video_writer is None:
                    h, w = frame.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    # The step loop runs at roughly 10fps
                    self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, 10.0, (w, h))
                # Convert RGB (from picamera2) to BGR (for OpenCV)
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                self.video_writer.write(bgr_frame)
                
            return frame
        else:
            print("Picamera2 not available")
            return None

    def close(self):
        self.stop_recording()
        if PICAM_AVAILABLE:
            self.picam2.stop()
            print("Camera closed.")
        else:
            print("Picamera2 not available")