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
            
    def record_video(self, duration=5, filename=None):
        """Records a video independently for a given duration."""
        if not PICAM_AVAILABLE:
            print("Picamera2 not available")
            return
            
        if filename is None:
            filename = "/home/admin/Documents/GitHub/edge/app/web/static/video.avi"
        else:
            filename = f"/home/admin/Documents/GitHub/edge/app/web/static/{filename}"
        
        print(f"Recording video to {filename} for {duration} seconds...")
        
        frame = self.picam2.capture_array()
        if frame is None:
            print("Failed to capture frame for video.")
            return
            
        h, w = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 10.0
        video_writer = cv2.VideoWriter(filename, fourcc, fps, (w, h))
        
        start_time = time.time()
        while (time.time() - start_time) < duration:
            frame = self.picam2.capture_array()
            if frame is not None:
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video_writer.write(bgr_frame)
            time.sleep(1.0 / fps)
            
        video_writer.release()
        print(f"Stopped video recording. Saved to {filename}")
            
    def capture_array(self):
        """Captures an image directly to memory as a numpy array."""
        if PICAM_AVAILABLE:
            frame = self.picam2.capture_array()
            return frame
        else:
            print("Picamera2 not available")
            return None

    def close(self):
        if PICAM_AVAILABLE:
            self.picam2.stop()
            print("Camera closed.")
        else:
            print("Picamera2 not available")