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
        self.navigator = Navigator(self.motion)

        self.alignment = Alignment(self.camera)
        self.pid = PID()

        self.is_running = False
        self.is_following_path = False   

    def start_forward_path(self):
        """Initiates a simple forward path using the camera feed."""
        self.is_following_path = True
        self.pid.integral = 0
        self.pid.prev_error = 0
        self.motion.send_velocity(0.5, 0.0)
        print("Started forward path...")

    def stop_forward_path(self):
        """Stops the forward path mode."""
        self.is_following_path = False
        self.motion.send_velocity(0.0, 0.0)
        print("Stopped forward path.")

    def start(self):
        self.start_forward_path()
        self.is_running = True
        print("ScanController is running...")

    def stop(self):
        self.is_running = False
        self.stop_forward_path()
        print("ScanController is stopped...")
        
    def step(self):
        if self.is_following_path:
            self.follow_path_step()
            return

        if self.sensors.is_wall_ahead():
            self.navigator.handle_wall()
            self.motion.stop()  # Stop after handling wall
            return

        self.motion.move_forward_tile()
        self.inspect()
        self.motion.stop()  # Stop after moving and inspecting

    def follow_path_step(self):
        error = self.alignment.get_error()
        if error is None:
            self.motion.send_velocity(0.3, 0.0)  # Move forward if no error info
            return
        
        angular_velocity = self.pid.compute(error)
        
        self.motion.send_velocity(0.3, angular_velocity)
        
    def inspect(self):
        self.solenoid.tap()
        audio = self.mic.record()
        image = self.camera.capture()

        print(f"Processing {audio}, {image}")
        