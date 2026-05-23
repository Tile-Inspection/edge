from navigation.analyze import analyze, calculate_error, smooth_line
from constants import X_DIM, Y_DIM
from hardware.camera import Camera

class Alignment:
    def __init__(self, camera: Camera):
        self.camera = camera     
        
        self.prev_bottom = None
        self.prev_left = None
        self.prev_right = None
        
        print(f'Alignment initialized. Initial error is {self.get_error()}')
    
    def get_error(self):
        """Captures an image, analyzes lines, and calculates the error for path following."""
        frame = self.camera.capture_array()
        if frame is None:
            return
        
        _, _, left_line, right_line = analyze(frame, X_DIM, Y_DIM)
        
        best_left_line = smooth_line(self.prev_left, left_line, X_DIM, Y_DIM)
        best_right_line = smooth_line(self.prev_right, right_line, X_DIM, Y_DIM)
        
        # Update state
        self.prev_left = best_left_line
        self.prev_right = best_right_line
        
        print('Calculating error...')  
        _, _, angle_error, _, _, _ = calculate_error(best_left_line, best_right_line, image_width=X_DIM, image_height=Y_DIM)
        print(f'Error: get_steer_cmd_degrees: {angle_error}')
        return angle_error
        