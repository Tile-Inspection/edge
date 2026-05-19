import csv
import os
import time

from hardware.encoder import WheelEncoder
from hardware.mpu6050 import MPU6050
from movement.alignment import Alignment
from hardware.servo import SprayerServo
from movement.pid import PID
from hardware.motion import Motion
from hardware.sensors import Sensors
from hardware.solenoid import Solenoid
from hardware.camera import Camera
from hardware.microphone import Microphone
from protocol.serial import SerialCommunicator
from movement.navigator import Navigator

class ScanController:
    def __init__(self):
        self.serial_communicator = SerialCommunicator()
        
        self.motion = Motion(self.serial_communicator)
        self.sensors = Sensors()
        self.solenoid = Solenoid()
        self.sprayer = SprayerServo()
        self.camera = Camera()
        self.mic = Microphone()
        self.mpu6050 = MPU6050()
        self.left_encoder = WheelEncoder(pin=13, vcc_pin=12)
        self.right_encoder = WheelEncoder(pin=5, vcc_pin=7)
        self.alignment = Alignment(self.camera)
        self.navigator = Navigator(self.motion, self.mpu6050, self.left_encoder, self.right_encoder, self.alignment)

        self.pid = PID()

        self.is_running = False
        self.is_following_path = False   
        self.tile_size = 0.3  # Default tile size in meters

    def start_forward_path(self):
        """Initiates a simple forward path using the camera feed."""
        # self.is_following_path = True
        self.pid.integral = 0
        self.pid.prev_error = 0
        self.motion.send_velocity(0.5, 0.0)
        print("Started forward path...")

    def stop_forward_path(self):
        """Stops the forward path mode."""
        # self.is_following_path = False
        self.motion.send_velocity(0.0, 0.0)
        print("Stopped forward path.")

    def start(self, rows: int, cols: int, tile_size: float):
        self.tile_size = tile_size
        self.is_running = True
        self.start_scan_sequence(rows, cols)
        # self.start_forward_path()
        print("ScanController is running...")

    def stop(self):
        self.is_running = False
        # self.stop_forward_path()
        print("ScanController is stopped...")
        
    def step(self):
        if self.is_following_path:
            self.follow_path_step()
            return

        self.navigator.forward_distance(speed=0.1, distance_meters=self.tile_size)
        self.motion.stop()  # Stop after moving and inspecting
        time.sleep(0.5)  # Small delay to ensure movement is completed before inspection
        self.inspect()
        
    def start_scan_sequence(self, rows: int, cols: int):
        print(f"Starting scan sequence with {rows} rows and {cols} cols...")
        self.inspect()
        for col in range(cols):
            for row in range(rows):
                if not self.is_running:
                    print("Scan sequence stopped.")
                    return
                print(f"Scanning tile at row {row}, col {col}...")
                self.step()
            # After each row, you can add logic to turn or reposition as needed
            if col < cols - 1:  # Don't turn after the last row
                self.navigator.forward_distance(speed=0.1, distance_meters=0.13)
                time.sleep(0.5)
                self.navigator.turn_right_90()
                time.sleep(0.5)  # Small delay to ensure turn is completed
                self.navigator.forward_distance(speed=0.1, distance_meters=0.15)
                time.sleep(0.5)
                self.inspect()
                time.sleep(0.5)
                self.navigator.forward_distance(speed=0.1, distance_meters=0.13)
                time.sleep(0.5)
                self.navigator.turn_right_90()
                time.sleep(0.5)
                self.navigator.forward_distance(speed=0.1, distance_meters=0.15)
                time.sleep(0.5)  # Small delay to ensure turn is completed
                self.inspect()
                time.sleep(0.5)
        print("Completed scan sequence.")

    def follow_path_step(self):
        error = self.alignment.get_error()
        angular_velocity = 0.0
        if error is None:
            angular_velocity = 0.0
        else:
            angular_velocity = self.pid.compute(error)
        
        # Log the error, linear velocity and angular velocity for debugging
        log_file = "debug_log.csv"
        file_exists = os.path.isfile(log_file)
        try:
            print('trying writing to csv')
            with open(log_file, "a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists or os.path.getsize(log_file) == 0:
                    writer.writerow(["timestamp", "error", "linear_velocity", "angular_velocity"])
                writer.writerow([time.time(), error, 0.5, angular_velocity])
        except Exception as e:
            print(f"Error logging to CSV: {e}")

        self.motion.send_velocity(0.5, angular_velocity)
        
    def inspect(self):
        self.solenoid.tap()
        # audio = self.mic.record()
        image = self.camera.capture()

        print(f"Processing {image}")
