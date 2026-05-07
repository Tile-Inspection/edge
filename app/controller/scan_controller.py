from hardware.motion import Motion
from hardware.sensors import Sensors
from hardware.solenoid import Solenoid
from hardware.camera import Camera
from hardware.microphone import Microphone
from hardware.serial import SerialCommunicator
from navigator.navigator import Navigator
from navigation.analyze import analyze, calculate_error

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
        self.is_following_path = False
        
        # PID parameters
        self.kp = 0.01
        self.ki = 0.001
        self.kd = 0.005
        self.prev_error = 0
        self.integral = 0

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
            
        _, _, left_line, right_line = analyze(frame)
        
        # Default dimensions for the camera capture, adjust as necessary
        X_DIM = 640
        Y_DIM = 480
        
        error, _, _ = calculate_error(left_line, right_line, image_width=X_DIM, image_height=Y_DIM)
        
        print("Error: ", error)
        
        # PID calculation
        self.integral += error
        derivative = error - self.prev_error
        angular_velocity = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        
        # Clamp angular velocity to [-1.0, 1.0] bounds
        angular_velocity = max(-1.0, min(1.0, angular_velocity))
        
        self.prev_error = error
        
        self.serial_communicator.send_velocity(0.5, angular_velocity) # 0.5 is the base linear speed
        
    def inspect(self):
        self.solenoid.tap()
        audio = self.mic.record()
        image = self.camera.capture()

        print(f"Processing {audio}, {image}")
        