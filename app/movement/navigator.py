import time
import csv

from hardware.motion import Motion
from hardware.magnetometer import Magnetometer
from movement.pid import PID

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
            
        log_data = []
        
        # Log 1 second before the turn
        start_wait = time.time()
        while time.time() - start_wait < 1.0:
            heading = self.magnetometer.get_heading()
            log_data.append([time.time(), heading, 0.0])
            time.sleep(0.01)
            
        start_heading = self.magnetometer.get_heading()
        target_angle = 90.0
        
        tolerance = 2.0  # We can use a tighter tolerance now that it corrects itself
        
        pid = PID(kp=0.015, ki=0.0005, kd=0.001)
        while True:
            current_heading = self.magnetometer.get_heading()
            turned = (current_heading - start_heading) % 360
            
            # Handle backward sensor jitter wraps at the start of the turn
            if turned > 180:
                turned -= 360
                
            error = target_angle - turned
            if abs(error) <= tolerance:
                break
                
            speed = pid.compute(error)
            log_data.append([time.time(), current_heading, speed, error])
            
            print(f"Turn right PID - Error: {error:.2f}, Speed: {speed:.2f}, Heading: {current_heading:.2f}")
            
            if speed > 0:
                self.motion.turn_right(speed)
            else:
                self.motion.turn_left(-speed)
                
            time.sleep(0.01)
            
        self.motion.stop()
        
        # Log 1 second after the turn
        start_wait = time.time()
        while time.time() - start_wait < 1.0:
            heading = self.magnetometer.get_heading()
            log_data.append([time.time(), heading, 0.0, 0.0])
            time.sleep(0.01)
            
        # Write log data to CSV
        try:
            with open("turn_right_log.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "current_reading", "speed", "error"])
                writer.writerows(log_data)
            print("Turn right log saved to turn_right_log.csv")
        except Exception as e:
            print(f"Error saving turn log: {e}")

    def turn_left_90(self):
        """Turns the robot left by exactly 90 degrees using the magnetometer."""
        if not self.magnetometer or not self.magnetometer.bus:
            print("Magnetometer not available, falling back to time-based turn.")
            self.turn_left()
            return
            
        start_heading = self.magnetometer.get_heading()
        target_angle = 90.0
        
        tolerance = 2.0
        
        pid = PID()
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
