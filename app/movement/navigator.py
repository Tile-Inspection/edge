import time
from hardware.motion import Motion
from movement.alignment import Alignment
from movement.proportional import Proportional

ONE_TILE_DURATION = 1.0  # seconds to move one tile at full speed
TURN_DURATION = 0.5  # seconds to turn 90 degrees at full speed

class Navigator:
    def __init__(self, motion: Motion, alignment: Alignment, proportional: Proportional, 
                 left_encoder=None, right_encoder=None, mpu=None):
        self.motion = motion
        self.alignment = alignment
        self.proportional = proportional
        
        # Kept strictly for standalone API testing & fallback
        self.left_encoder = left_encoder
        self.right_encoder = right_encoder
        self.mpu = mpu
        
    def move_forward_tile(self, target_speed=0.5):
        """Moves forward one tile with gradual acceleration and active vision drift correction."""
        
        # Calculate base time needed. e.g., 1.0 duration / 0.5 speed = 2.0 seconds
        base_duration = ONE_TILE_DURATION / target_speed
        
        # Ramp-up parameters to smoothly start the motors
        ramp_duration = 0.75  # seconds to reach full target_speed
        
        # Add half the ramp duration to the total target duration to compensate 
        # for the lost distance while accelerating
        target_duration = base_duration + (ramp_duration / 2.0)

        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed >= target_duration:
                break
                
            # 1. Gradual speed calculation (Ramp up)
            if elapsed < ramp_duration:
                current_speed = target_speed * (elapsed / ramp_duration)
            else:
                current_speed = target_speed

            # 2. Vision Correction
            error = self.alignment.get_error()
            
            if error is None:
                angular_velocity = 0.0
            else:
                angular_velocity = self.proportional.compute(error)
                
            # 3. Apply movement
            self.motion.send_velocity(current_speed, angular_velocity)
            time.sleep(0.05)  # Restrict loop to ~20Hz to match camera processing
            
        self.motion.stop()

    def forward_distance(self, speed, distance_meters, steer_cmd_degrees=0.0):
        """
        Preserved hardware-based movement strictly for battery_test.py 
        and manual_control.py /test-encoder endpoints.
        """
        if self.left_encoder: self.left_encoder.reset()
        if self.right_encoder: self.right_encoder.reset()

        # Naive time fallback to support distance tracking (Adjust to your wheel diameter spec)
        duration = distance_meters / (speed * 0.5) if speed > 0 else 0
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            # Blind forward tracking based on test steer command
            self.motion.send_velocity(speed, steer_cmd_degrees / 90.0)
            time.sleep(0.1)
            
        self.motion.stop()
        
        l_ticks = self.left_encoder.get_ticks() if self.left_encoder else 0
        r_ticks = self.right_encoder.get_ticks() if self.right_encoder else 0
        
        return l_ticks, r_ticks

    def turn_right(self):
        speed = 0.5
        self.motion.turn_right(speed)
        time.sleep(TURN_DURATION * speed)
        self.motion.stop()

    def turn_left(self):
        speed = 0.5
        self.motion.turn_left(speed)
        time.sleep(TURN_DURATION * speed)
        self.motion.stop()
        
    def turn_right_90(self):
        self.turn_right()

    def turn_left_90(self):
        self.turn_left()

    def forward(self, speed, duration):
        self.motion.forward(speed)
        time.sleep(duration)
        self.motion.stop()
        
    def right(self, speed, duration):
        self.motion.turn_right(speed)
        time.sleep(duration)
        self.motion.stop()

    def left(self, speed, duration):
        self.motion.turn_left(speed)
        time.sleep(duration)
        self.motion.stop()