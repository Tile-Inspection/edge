from hardware.motion import Motion
from hardware.sensors import Sensors
from hardware.solenoid import Solenoid
from hardware.camera import Camera
from hardware.microphone import Microphone
from hardware.serial import SerialCommunicator
from navigation.navigator import Navigator

class ScanController:
    def __init__(self):        
        self.serial_communicator = SerialCommunicator()
        
        self.motion = Motion(self.serial_communicator)
        self.sensors = Sensors()
        self.solenoid = Solenoid()
        self.camera = Camera()
        self.mic = Microphone()
        self.navigator = Navigator(self.motion)

        self.is_running = False

    def start(self):
        self.is_running = True
        print("ScanController is running...")

    def stop(self):
        self.is_running = False
        print("ScanController is stopped...")
        
    def step(self):
        if self.sensors.is_wall_ahead():
            self.navigator.handle_wall()
            self.serial_communicator.send_command("S")  # Stop after handling wall
            return

        self.motion.move_forward_tile()
        self.inspect()
        self.serial_communicator.send_command("S")  # Stop after moving and inspecting
        
    def inspect(self):
        self.solenoid.tap()
        audio = self.mic.record()
        image = self.camera.capture()

        print(f"Processing {audio}, {image}")
        