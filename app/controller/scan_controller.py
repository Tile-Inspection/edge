import csv
import os
import time
import cv2

from db.database import get_db
from db.models import Result
from deployment.inference import classify_live_tap
from crack_detection.process_image_frame import predict

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
from hardware.buttons import PhysicalButtons

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
        self.physical_buttons = PhysicalButtons(pin1=10, pin2=9, pin3=11)

        self.pid = PID()

        self.is_running = False
        self.is_following_path = False   
        self.tile_size = 0.3  # Default tile size in meters
        self.current_scan_id = None

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

    def start(self, rows: int, cols: int, tile_size: float, scan_id: int):
        self.tile_size = tile_size
        self.is_running = True
        self.current_scan_id = scan_id
        self.start_scan_sequence(rows, cols)
        # self.start_forward_path()
        print("ScanController is running...")

    def stop(self):
        self.is_running = False
        # self.stop_forward_path()
        print("ScanController is stopped...")

    def start_scan_sequence(self, rows: int, cols: int):
        """
        Starts a serpentine scan pattern. The original implementation was flawed and
        did not correctly traverse a grid, so it has been replaced with this
        more robust version.

        - It inspects the tile it's currently on.
        - It moves forward one tile at a time for a column.
        - At the end of a column, it performs a U-turn to the next column.
        - It alternates going "down" (increasing row index) and "up" (decreasing row index).
        """
        print(f"Starting scan sequence for a {rows}x{cols} grid...")
        self.navigator.forward_distance(speed=1, distance_meters=self.tile_size+0.1)
        time.sleep(0.5)
        self.navigator.turn_right_90()
        time.sleep(0.5)
        self.navigator.forward_distance(speed=0.5, distance_meters=-0.10)
        time.sleep(0.5)

        for col in range(cols):
            # Determine direction for this column (down for even cols, up for odd cols)
            is_going_down = col % 2 == 0
            row_range = range(rows) if is_going_down else range(rows - 1, -1, -1)

            for row in row_range:
                if not self.is_running:
                    print("Scan sequence stopped.")
                    return
                
                print(f"Scanning tile at ({col}, {row})...")
                self.inspect(x=col, y=row)
                
                # Check if it's the last tile in the column to avoid moving after inspection
                is_last_tile_in_col = (is_going_down and row == rows - 1) or \
                                      (not is_going_down and row == 0)

                if not is_last_tile_in_col:
                    # Move to next tile in the same column
                    print(f"Moving to next tile in column {col}...")
                    self.navigator.forward_distance(speed=1, distance_meters=self.tile_size)
                    time.sleep(0.5)

            # After a column is finished, transition to the next one if it's not the last column
            if col < cols - 1:  # Don't turn after the last row
                print(f"Transitioning from column {col} to {col + 1}...")
                # Perform a U-turn to position for the next column.
                # This simple U-turn moves to the side by one tile width.
                self.navigator.forward_distance(speed=0.5, distance_meters=0.10)
                time.sleep(0.5)
                self.navigator.turn_right_90()
                time.sleep(0.5)
                self.navigator.forward_distance(speed=0.5, distance_meters=self.tile_size - 0.05)
                time.sleep(0.5)
                self.navigator.turn_right_90()
                time.sleep(0.5)
                self.navigator.forward_distance(speed=0.5, distance_meters=-0.13)
                time.sleep(0.5)

        self.is_running = False
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
        
    def inspect(self, x: int, y: int):
        if self.current_scan_id is None:
            print("Warning: inspect called without a scan_id. Skipping database record.")
            return

        self.solenoid.tap()

        # Filenames are relative to the static dir for serving via the web server.
        base_name = f"scan_{self.current_scan_id}_tile_{x}_{y}"
        img_filename = f"{base_name}.jpg"
        aud_filename = f"{base_name}.wav"
        
        # These methods save files and return the full path.
        image_path = self.camera.capture(filename=img_filename)
        audio_path = self.mic.record(duration=1, filename=aud_filename)

        print(f"Captured {image_path} and {audio_path}")

        # The web server serves from the 'static' folder, so we need relative paths for the DB.
        rel_image_path = f"/{os.path.basename(image_path)}" if image_path else None
        rel_audio_path = f"/{os.path.basename(audio_path)}" if audio_path else None

        classification_data = None
        if audio_path:
            print(f"Predicting audio for {audio_path}...")
            try:
                prediction = classify_live_tap(audio_path)
                classification_data = {"type": prediction}
            except Exception as e:
                print(f"Error classifying audio: {e}")

        crack_classification_data = None
        if image_path:
            print(f"Predicting cracks for {image_path}...")
            try:
                crack_classification_data = predict(image_path)
            except Exception as e:
                print(f"Error classifying cracks: {e}")

        # Save result to the database
        with get_db() as db:
            db_result = Result(
                scan_id=self.current_scan_id,
                x=x,
                y=y,
                status="scanned",
                hollow_classification=classification_data,
                cracked_classification=crack_classification_data,
                image_file_path=rel_image_path,
                audio_file_path=rel_audio_path
            )
            db.add(db_result)
            db.commit()
            print(f"Saved result for ({x},{y}) to database.")
