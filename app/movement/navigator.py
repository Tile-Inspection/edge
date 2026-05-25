


import time
import math

import csv

from movement.alignment import Alignment
from hardware.encoder import WheelEncoder
from hardware.motion import Motion
from hardware.mpu6050 import MPU6050
from movement.pid import PID
from movement.proportional import Proportional

ONE_TILE_DURATION = 1.0  # seconds to move one tile at full speed, adjust as needed based on testing
TURN_DURATION = 0.5  # seconds to turn 90 degrees at full speed, adjust as needed based on testing

class Navigator:
    def __init__(self, motion: Motion, mpu6050: MPU6050, left_encoder: WheelEncoder, right_encoder: WheelEncoder, alignment: Alignment, enable_grout_correction=False):
        self.motion = motion
        self.mpu6050 = mpu6050
        self.left_encoder = left_encoder
        self.right_encoder = right_encoder
        self.alignment = alignment
        self.enable_grout_correction = enable_grout_correction
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
        target_angle = 78
        
        tolerance = 1
        
        # Kp is higher because the Proportional class now normalizes the error 
        # up to 90 degrees before applying the x^3 curve.
        pid = Proportional(kp=2.5)
        while True:
            current_heading = self.mpu6050.get_heading()
            turned = abs(current_heading)
            
            error = target_angle - turned
            
            speed = pid.compute(error)
            
            if abs(error) <= tolerance:
                break
                
            # Clamp max speed to reduce momentum, and min speed to prevent stalling
            clamped_speed = max(0.2, min(1, abs(speed)))

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
        target_angle = 81
        
        tolerance = 1
        
        pid = Proportional(kp=2.5)
        while True:
            current_heading = self.mpu6050.get_heading()
            turned = abs(current_heading)

            error = target_angle - turned
            if abs(error) <= tolerance:
                break
                
            speed = pid.compute(error)
            
            clamped_speed = max(0.2, min(1, abs(speed)))

            if speed > 0:
                self.motion.turn_left(clamped_speed)
            else:
                self.motion.turn_right(clamped_speed)
                
            time.sleep(0.01)
            
        self.motion.stop()
        
    def forward_distance(self, speed, distance_meters, steer_cmd_degrees=0.0):
        """Moves robot forward a specific distance using pre-compensated steering + short feedback correction."""

        # Direction handling
        direction = -1 if distance_meters < 0 or speed < 0 else 1
        actual_speed = abs(speed) * direction
        actual_distance = abs(distance_meters)

        ticks_per_meter = 143.51
        target_ticks = actual_distance * ticks_per_meter

        # ============================
        # PD FEEDBACK CONTROL
        # ============================

        kp = 0.015  # Tuned for degree error scale instead of encoder ticks
        kd = 0.005  # Derivative gain to prevent oscillation
        max_angular = abs(actual_speed) * 0.8

        self.left_encoder.reset()
        self.right_encoder.reset()

        prev_error = 0.0

        while True:
            left_ticks = self.left_encoder.get_ticks()
            right_ticks = self.right_encoder.get_ticks()

            avg_ticks = (left_ticks + right_ticks) / 2.0

            if avg_ticks >= target_ticks:
                break

            # Fetch dynamic steering error
            current_error = 0.0
            if self.enable_grout_correction:
                err = self.alignment.get_error()
                if err is not None:
                    current_error = err
            else:
                current_error = steer_cmd_degrees  # Fallback to static command
                
            # Safety check - stop if completely lost (error > 45)
            if abs(current_error) > 45:
                print("Steer error too large. Stopping.")
                break
                
            # Deadband for noisy perfectly-aligned state (fluctuates between 0 and 2)
            if abs(current_error) <= 2.0:
                current_error = 0.0

            # PD Controller calculation
            derivative = current_error - prev_error
            angular_velocity = (current_error * kp + derivative * kd) * direction
            prev_error = current_error

            # clamp
            angular_velocity = max(-max_angular, min(max_angular, angular_velocity))

            print(f"Left: {left_ticks}; Right: {right_ticks}\tError: {current_error:.2f}\tAngVel: {angular_velocity:.3f}")

            self.motion.send_velocity(actual_speed, angular_velocity)

            # Avoid pegging CPU if we aren't querying the camera dynamically
            if not self.enable_grout_correction:
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
