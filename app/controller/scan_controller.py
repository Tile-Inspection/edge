from hardware.adc import ADC
from controller.pid import PID
from hardware.motion import Motion
from hardware.sensors import Sensors
from hardware.solenoid import Solenoid
from hardware.camera import Camera
from hardware.microphone import Microphone
from hardware.serial import SerialCommunicator
from navigator.navigator import Navigator
from navigation.analyze import analyze, calculate_error, smooth_line
from constants import X_DIM, Y_DIM

class ScanController:
    def __init__(self):
        self.serial_communicator = SerialCommunicator()
        
        self.motion = Motion(self.serial_communicator)
        self.sensors = Sensors()
        self.solenoid = Solenoid()
        self.camera = Camera()
        self.mic = Microphone()
        self.navigator = Navigator(self.motion)

        self.pid = PID()
        self.adc = ADC(channel=3)

        self.is_running = False
        self.is_following_path = False        
        
        self.prev_bottom = None
        self.prev_left = None
        self.prev_right = None

    def start_forward_path(self):
        """Initiates a simple forward path using the camera feed."""
        self.is_following_path = True
        self.integral = 0
        self.prev_error = 0
        self.serial_communicator.send_velocity(0.5, 0.0)
        print("Started forward path...")

    def stop_forward_path(self):
        """Stops the forward path mode."""
        self.is_following_path = False
        self.serial_communicator.send_velocity(0.0, 0.0)
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
            self.serial_communicator.send_command("S")  # Stop after handling wall
            return

        self.motion.move_forward_tile()
        self.inspect()
        self.serial_communicator.send_command("S")  # Stop after moving and inspecting

    def follow_path_step(self):
        """Captures an image, analyzes lines, and calculates PID correction."""
        frame = self.camera.capture_array()
        if frame is None:
            return
        
        _, _, left_line, right_line = analyze(frame, X_DIM, Y_DIM)
        
        best_left_line = smooth_line(self.prev_left, left_line, X_DIM, Y_DIM)
        best_right_line = smooth_line(self.prev_right, right_line, X_DIM, Y_DIM)
        
        # Update state
        self.prev_left = best_left_line
        self.prev_right = best_right_line
        
        error, _, _ = calculate_error(best_left_line, best_right_line, image_width=X_DIM, image_height=Y_DIM)
        
        angular_velocity = self.pid.compute(error)
        
        self.serial_communicator.send_velocity(0.5, angular_velocity) # 0.5 is the base linear speed
        
    def inspect(self):
        self.solenoid.tap()
        audio = self.mic.record()
        image = self.camera.capture()

        print(f"Processing {audio}, {image}")
        