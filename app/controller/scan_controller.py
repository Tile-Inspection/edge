import csv
import os
import time

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

        self.alignment = Alignment(self.camera)
        self.pid = PID()
        
        # Inject alignment and PID directly into the Navigator
        self.navigator = Navigator(self.motion, self.alignment, self.pid)

        self.is_running = False

    def start(self):
        self.is_running = True
        print("ScanController is running...")

    def stop(self):
        self.is_running = False
        self.motion.stop()
        print("ScanController is stopped...")
        
    def step(self):
        # 1. Check for physical walls
        if self.sensors.is_wall_ahead():
            print("Wall detected ahead. Stopping scan.")
            self.motion.stop() 
            self.is_running = False
            return

        # 2. Move forward one tile using the closed-loop vision drift correction
        self.navigator.move_forward_tile()
        
        # 3. Inspect the current tile
        self.inspect()
        
    def inspect(self):
        self.solenoid.tap()
        audio = self.mic.record()
        image = self.camera.capture()

        print(f"Processing {audio}, {image}")