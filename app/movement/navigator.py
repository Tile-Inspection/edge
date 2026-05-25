import time
from hardware.motion import Motion
from movement.alignment import Alignment
from movement.pid import PID

ONE_TILE_DURATION = 1.0  # seconds to move one tile at full speed
TURN_DURATION = 0.5  # seconds to turn 90 degrees at full speed

class Navigator:
    def __init__(self, motion: Motion, alignment: Alignment, pid: PID):
        self.motion = motion
        self.alignment = alignment
        self.pid = pid
        self.turn_right_next = True 
        
    def move_forward_tile(self):
        """Moves forward one tile while actively correcting drift using camera vision."""
        speed = 0.5
        target_duration = ONE_TILE_DURATION * speed
        
        # Reset PID integral and error to prevent windup from previous tile
        self.pid.integral = 0
        self.pid.prev_error = 0

        start_time = time.time()
        while (time.time() - start_time) < target_duration:
            error = self.alignment.get_error()
            
            # If line is lost momentarily, drive straight. Otherwise, apply correction.
            if error is None:
                angular_velocity = 0.0
            else:
                angular_velocity = self.pid.compute(error)
                
            self.motion.send_velocity(speed, angular_velocity)
            time.sleep(0.05)  # Restrict loop to ~20Hz to match camera frame processing
            
        self.motion.stop()

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
        
    # Time-based fallbacks for the API endpoints since the magnetometer is removed
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