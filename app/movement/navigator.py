import time
import csv

from hardware.encoder import WheelEncoder
from hardware.motion import Motion
from hardware.magnetometer import Magnetometer
from movement.pid import PID
from movement.proportional import Proportional

ONE_TILE_DURATION = 1.0  # seconds to move one tile at full speed, adjust as needed based on testing
TURN_DURATION = 0.5  # seconds to turn 90 degrees at full speed, adjust as needed based on testing

class Navigator:
    def __init__(self, motion: Motion, magnetometer: Magnetometer, left_encoder: WheelEncoder, right_encoder: WheelEncoder):
        self.motion = motion
        self.magnetometer = magnetometer
        self.left_encoder = left_encoder
        self.right_encoder = right_encoder
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
        
        tolerance = 2.0  # We can use a tighter tolerance now that it corrects itself
        
        pid = Proportional()
        while True:
            current_heading = self.magnetometer.get_heading()
            turned = (current_heading - start_heading) % 360
            
            # Handle backward sensor jitter wraps at the start of the turn
            if turned > 180:
                turned -= 360
            
            error = target_angle - turned
            
            speed = pid.compute(error)
            
            if abs(error) <= tolerance:
                break
                
            if speed > 0:
                self.motion.turn_right(speed)
            else:
                self.motion.turn_left(-speed)
                
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
        
        tolerance = 2.0
        
        pid = Proportional()
        while True:
            current_heading = self.magnetometer.get_heading()
            turned = (start_heading - current_heading) % 360
            
            if turned > 180:
                turned -= 360
                
            error = target_angle - turned
            if abs(error) <= tolerance:
                break
                
            speed = pid.compute(error)
            
            if speed > 0:
                self.motion.turn_left(speed)
            else:
                self.motion.turn_right(-speed)
                
            time.sleep(0.01)
            
        self.motion.stop()
        
    def forward_distance(self, speed, distance_meters):
        """Moves the robot forward a specific distance in meters."""
        kp = 0.00 
        max_angular = speed * 0.4  # Max angular velocity proportional to speed
        
        ticks_per_meter = 187.5  # This should be calibrated based on the robot's wheel and encoder
        target_ticks = distance_meters * ticks_per_meter
        
        self.left_encoder.reset()
        self.right_encoder.reset()
                
        while True:
            left_ticks = self.left_encoder.get_ticks()
            right_ticks = self.right_encoder.get_ticks()
            
            avg_ticks = (left_ticks + right_ticks) / 2.0
            
            if avg_ticks >= target_ticks:
                break
                
            # If left wheel has more ticks than right, the robot is veering right.
            # We want to turn left (angular < 0 in motion.py).
            # error will be negative if left > right.
            error = right_ticks - left_ticks
            angular_velocity = error * kp
            
            # Clamp angular velocity to prevent wild swinging
            angular_velocity = max(-max_angular, min(max_angular, angular_velocity))
            
            self.motion.send_velocity(speed, angular_velocity)
            
            time.sleep(0.02)
            
        self.motion.stop()
        
        return self.left_encoder.get_ticks(), self.right_encoder.get_ticks()
        

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
