import time

from hardware.motion import Motion
from hardware.magnetometer import Magnetometer

ONE_TILE_DURATION = 1.0  # seconds to move one tile at full speed, adjust as needed based on testing
TURN_DURATION = 0.5  # seconds to turn 90 degrees at full speed, adjust as needed based on testing

class Navigator:
    def __init__(self, motion: Motion, magnetometer: Magnetometer):
        self.motion = motion
        self.magnetometer = magnetometer
        self.turn_right_next = True  # alternate turns
        
    def move_forward_tile(self):
        """Moves the robot forward by one tile."""
        speed = 0.5  # Move at half speed for better control
        self.motion.forward(speed)
        time.sleep(ONE_TILE_DURATION * speed)  # Move for the duration needed to cover one tile
        self.motion.stop()

    def turn_right(self):
        """Turns the robot right by 90 degrees."""
        speed = 0.5
        self.motion.turn_right(speed)
        time.sleep(TURN_DURATION * speed)  # Adjust this duration based on testing to achieve a 90 degree turn
        self.motion.stop()

    def turn_left(self):
        """Turns the robot left by 90 degrees."""
        speed = 0.5
        self.motion.turn_left(speed)
        time.sleep(TURN_DURATION * speed)  # Adjust this duration based on testing to achieve a 90 degree turn
        self.motion.stop()
        
    def turn_right_90(self):
        """Turns the robot right by exactly 90 degrees using the magnetometer."""
        if not self.magnetometer or not self.magnetometer.bus:
            print("Magnetometer not available, falling back to time-based turn.")
            self.turn_right()
            return
            
        start_heading = self.magnetometer.get_heading()
        target_angle = 90.0
        
        # Proportional controller constants
        kp = 0.015       # Proportional gain
        min_speed = 0.25 # Minimum speed to overcome friction
        max_speed = 0.5  # Maximum turning speed
        tolerance = 2.0  # Stop when within 2 degrees of target
        
        while True:
            current_heading = self.magnetometer.get_heading()
            turned = (current_heading - start_heading) % 360
            
            # Handle backward sensor jitter wraps at the start of the turn
            if turned > 180:
                turned -= 360
                
            error = target_angle - turned
            if error <= tolerance:
                break
                
            # Calculate speed based on remaining error and clamp it between min/max
            speed = kp * error
            speed = max(min_speed, min(max_speed, speed))
            
            self.motion.turn_right(speed)
            time.sleep(0.01)
            
        self.motion.stop()

    def turn_left_90(self):
        """Turns the robot left by exactly 90 degrees using the magnetometer."""
        if not self.magnetometer or not self.magnetometer.bus:
            print("Magnetometer not available, falling back to time-based turn.")
            self.turn_left()
            return
            
        start_heading = self.magnetometer.get_heading()
        target_angle = 90.0
        
        kp = 0.015
        min_speed = 0.25
        max_speed = 0.5
        tolerance = 2.0
        
        while True:
            current_heading = self.magnetometer.get_heading()
            turned = (start_heading - current_heading) % 360
            
            if turned > 180:
                turned -= 360
                
            error = target_angle - turned
            if error <= tolerance:
                break
                
            speed = kp * error
            speed = max(min_speed, min(max_speed, speed))
            
            self.motion.turn_left(speed)
            time.sleep(0.01)
            
        self.motion.stop()

    ## [START] TESTING/CALIBRATION FUNCTIONS
    def forward(self, speed, duration):
        """Moves the robot forward for the specified duration."""
        self.motion.forward(speed)
        time.sleep(duration)
        self.motion.stop()
        
    def right(self, speed, duration):
        """Moves the robot right for the specified duration."""
        self.motion.turn_right(speed)
        time.sleep(duration)
        self.motion.stop()

    def left(self, speed, duration):
        """Moves the robot left for the specified duration."""
        self.motion.turn_left(speed)
        time.sleep(duration)
        self.motion.stop()
    ## [END] TESTING/CALIBRATION FUNCTIONS
