import time

# Hardware
from hardware.motion import Motion
from hardware.sensors import Sensors
from hardware.solenoid import Solenoid
from hardware.servo import SprayerServo
from hardware.camera import Camera
from hardware.microphone import Microphone
from protocol.serial import SerialCommunicator
from hardware.mpu6050 import MPU6050
from hardware.encoder import WheelEncoder

# Movement & Vision
from movement.alignment import Alignment
from movement.proportional import Proportional
from movement.navigator import Navigator

# AI Models
from models.crack_detector import CrackDetector
from models.sound_classifier import SoundClassifier


class ScanController:
    def __init__(self, enable_audio=False, enable_crack=False, enable_grout_correction=False):
        self.serial_communicator = SerialCommunicator()
        self.motion = Motion(self.serial_communicator)
        self.sensors = Sensors()
        self.solenoid = Solenoid()
        self.sprayer = SprayerServo()
        self.camera = Camera()
        self.mic = Microphone()

        # 1. Conditionally initialize AI models so routes don't crash
        self.sound_classifier = SoundClassifier() if enable_audio else None
        self.crack_detector = CrackDetector() if enable_crack else None

        # 2. Preserve Hardware for `manual_control.py` API tests
        self.mpu6050 = MPU6050()
        self.left_encoder = WheelEncoder(pin=27)  
        self.right_encoder = WheelEncoder(pin=22) 

        # 3. Inject Pure Vision Navigation
        self.alignment = Alignment(self.camera)
        self.proportional = Proportional(kp=0.1, max_error=90.0)

        self.navigator = Navigator(
            motion=self.motion, 
            alignment=self.alignment, 
            proportional=self.proportional,
            left_encoder=self.left_encoder,
            right_encoder=self.right_encoder,
            mpu=self.mpu6050
        )

        self.is_running = False

    def start(self, rows, cols, tile_size, scan_id):
        self.is_running = True
        print(f"ScanController is running... Scan ID: {scan_id}")
        
        while self.is_running:
            self.step()

    def stop(self):
        self.is_running = False
        self.motion.stop()
        print("ScanController is stopped...")
        
    def step(self):
        if self.sensors.is_wall_ahead():
            print("Wall detected ahead. Stopping scan.")
            self.motion.stop() 
            self.is_running = False
            return

        # Move forward using pure vision drift correction
        self.navigator.move_forward_tile()
        self.inspect()
        
    def inspect(self):
        self.solenoid.tap()
        audio = self.mic.record()
        image = self.camera.capture()

        print(f"Processing {audio}, {image}")
        
        if self.sound_classifier:
            self.sound_classifier.predict(audio)
            
        if self.crack_detector:
            self.crack_detector.predict(image)
            
        # Post-tap delay: Holds the robot still before the next movement starts
        print("Inspection complete. Delaying before proceeding to the next tile...")
        time.sleep(1.5)  # Adjust this value (in seconds) to tune your desired delay