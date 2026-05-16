from protocol.serial import SerialCommunicator

class Motion:
    def __init__(self, serial_communicator: SerialCommunicator=None):
        self.serial = serial_communicator
    
    @staticmethod
    def _format_velocity_command(linear: float, angular: float) -> bytes:
        """Format a velocity command as <v,w>."""
        payload = f"{linear},{angular}"
        return b"<" + payload.encode() + b">"
    
    def send_velocity(self, linear: float, angular: float):
        """Updates the current command using the new velocity protocol."""
        self.serial.set_command(self._format_velocity_command(linear, angular))
        
    def stop(self):
        """Sends a stop command to the robot."""
        self.send_velocity(0, 0)
        
    def forward(self, speed: float):
        assert 0 <= speed <= 1, "Speed must be between 0 and 1"
        self.send_velocity(speed, 0)
        
    def backward(self, speed: float):
        assert 0 <= speed <= 1, "Speed must be between 0 and 1"
        self.send_velocity(-speed, 0)
        
    def turn_left(self, speed: float):
        assert 0 <= speed <= 1, "Speed must be between 0 and 1"
        self.send_velocity(0, -speed)
        
    def turn_right(self, speed: float):
        assert 0 <= speed <= 1, "Speed must be between 0 and 1"
        self.send_velocity(0, speed)
    