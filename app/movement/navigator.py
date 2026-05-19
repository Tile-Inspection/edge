


import time


import csv

from hardware.encoder import WheelEncoder
from hardware.motion import Motion
from hardware.mpu6050 import MPU6050
from movement.pid import PID
from movement.proportional import Proportional

ONE_TILE_DURATION = 1.0  # seconds to move one tile at full speed, adjust as needed based on testing
TURN_DURATION = 0.5  # seconds to turn 90 degrees at full speed, adjust as needed based on testing

class Navigator:
    def __init__(self, motion: Motion, mpu6050: MPU6050, left_encoder: WheelEncoder, right_encoder: WheelEncoder):
        self.motion = motion
        self.mpu6050 = mpu6050
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
        """Turns the robot right by exactly 90 degrees using the MPU6050."""
        if not self.mpu6050 or not self.mpu6050.bus:
            print("MPU6050 not available, falling back to time-based turn.")
            self.turn_right()
            return
            
        self.mpu6050.reset_heading()
        # Target slightly less than 90 to account for inertia/momentum coasting
        target_angle = 80
        
        tolerance = 2
        
        # Lower Kp for a gentler approach curve
        pid = Proportional(kp=0.05)
        while True:
            current_heading = self.mpu6050.get_heading()
            turned = abs(current_heading)
            
            error = target_angle - turned
            
            speed = pid.compute(error)
            
            if abs(error) <= tolerance:
                break
                
            # Clamp max speed to reduce momentum, and min speed to prevent stalling
            clamped_speed = max(0.5, min(1, abs(speed)))

            print(f'Error {error}; Speed {speed}')

            if speed > 0:
                self.motion.turn_right(clamped_speed)
            else:
                self.motion.turn_left(clamped_speed)
                
            time.sleep(0.01)
            
        self.motion.stop()

    def turn_left_90(self):
        """Turns the robot left by exactly 90 degrees using the MPU6050."""
        if not self.mpu6050 or not self.mpu6050.bus:
            print("MPU6050 not available, falling back to time-based turn.")
            self.turn_left()
            return
            
        self.mpu6050.reset_heading()
        target_angle = 80
        
        tolerance = 2
        
        pid = Proportional(kp=0.05)
        while True:
            current_heading = self.mpu6050.get_heading()
            turned = abs(current_heading)

            error = target_angle - turned
            if abs(error) <= tolerance:
                break
                
            speed = pid.compute(error)
            
            clamped_speed = max(0.5, min(1, abs(speed)))

            if speed > 0:
                self.motion.turn_left(clamped_speed)
            else:
                self.motion.turn_right(clamped_speed)
                
            time.sleep(0.01)
            
        self.motion.stop()
        
    def forward_distance(self, speed, distance_meters, steer_cmd_degrees=0.0):
        """Moves the robot forward a specific distance in meters, gradually applying a steering correction."""
        import math
        
        kp = 0.1
        max_angular = speed * 0.8  # Max angular velocity proportional to speed
        
        ticks_per_meter = 178.24  # This should be calibrated based on the robot's wheel and encoder
        target_ticks = distance_meters * ticks_per_meter
        
        # --- Steering Correction Setup ---
        # The track width (distance between left and right wheels) in meters. 
        # You MUST measure this on your robot and update this variable!
        track_width_meters = 0.17  
        
        # Convert the steer command to radians
        steer_radians = math.radians(steer_cmd_degrees)
        
        # Total difference in distance the wheels need to travel to achieve the turn
        total_distance_diff = track_width_meters * steer_radians
        total_tick_diff = total_distance_diff * ticks_per_meter
        # ---------------------------------
        
        self.left_encoder.reset()
        self.right_encoder.reset()
                
        while True:
            left_ticks = self.left_encoder.get_ticks()
            right_ticks = self.right_encoder.get_ticks()
            
            avg_ticks = (left_ticks + right_ticks) / 2.0
            
            if avg_ticks >= target_ticks:
                break
                
            # Progressively apply the target tick difference based on how far we've moved
            progress = avg_ticks / target_ticks if target_ticks > 0 else 1.0
            current_target_diff = total_tick_diff * progress
            
            # If left wheel has more ticks than right, the robot is veering right.
            # We want to turn left (angular < 0 in motion.py).
            # error will be negative if left > right.
            # We subtract the current_target_diff so the controller smoothly allows the commanded turn
            error = (left_ticks - right_ticks) - current_target_diff
            angular_velocity = error * kp
            
            # Clamp angular velocity to prevent wild swinging
            angular_velocity = max(-max_angular, min(max_angular, angular_velocity))
            
            print(f'Left: {left_ticks}; Right:{right_ticks}	{angular_velocity}')

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
