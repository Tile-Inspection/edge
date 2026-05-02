import time

class Motion:
    def __init__(self, serial_communicator=None):
        self.serial = serial_communicator
    
    def move_forward_tile(self):
        if self.serial:
            self.serial.send_command("F")
        print("Moving forward 1 tile")
        # Assuming tile movement takes some time, but for now, just set command
        # In a real implementation, you might need to time this or wait for feedback
    
    def turn_left(self):
        if self.serial:
            self.serial.send_command("L")
        print("Turning LEFT 90°")
        # Simulate turn time
        time.sleep(0.5)  # Adjust based on actual turn time
        if self.serial:
            self.serial.send_command("S")  # Stop after turn
    
    def turn_right(self):
        if self.serial:
            self.serial.send_command("R")
        print("Turning RIGHT 90°")
        # Simulate turn time
        time.sleep(0.5)  # Adjust based on actual turn time
        if self.serial:
            self.serial.send_command("S")  # Stop after turn