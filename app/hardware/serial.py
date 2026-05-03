import serial
import threading
import time

class SerialCommunicator:
    def __init__(self):
        try:
            self.ser = serial.Serial(
                port='/dev/serial0',
                baudrate=74880,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            print("Serial port initialized successfully.")
        except serial.SerialException as e:
            print(f"Error initializing serial port: {e}")
            self.ser = None
        
        self.current_command = self._format_velocity_command(0, 0)  # Default to stop
        self.sending_thread = None
        self.running = False
        self.start_sending_loop()
    
    @staticmethod
    def _format_velocity_command(linear: float, angular: float) -> bytes:
        """Format a velocity command as <v,w>."""
        payload = f"{linear},{angular}"
        return b"<" + payload.encode() + b">"
    
    def start_sending_loop(self):
        """Starts a background thread that sends the current command at 10Hz."""
        if self.ser and not self.running:
            self.running = True
            self.sending_thread = threading.Thread(target=self._send_loop, daemon=True)
            self.sending_thread.start()
    
    def _send_loop(self):
        """Internal loop that sends the current command every 100ms."""
        while self.running:
            self._send_current_command()
            time.sleep(0.1)  # 10Hz = 0.1 seconds
    
    def _send_current_command(self):
        """Sends the current command to the serial device."""
        if self.ser and self.ser.is_open:
            if isinstance(self.current_command, str):
                payload = self.current_command.encode()
            else:
                payload = self.current_command
            self.ser.write(payload)
            print(f"Sent command: {payload}")
        else:
            print("Serial port is not open. Cannot send command.")
    
    def send_velocity(self, linear: float, angular: float):
        """Updates the current command using the new velocity protocol."""
        self.current_command = self._format_velocity_command(linear, angular)
        print(f"Updated current velocity command to: {self.current_command}")
    
    def send_command(self, command: str):
        """Updates the current command for legacy or raw serialized commands."""
        legacy_map = {
            "F": (1, 0),
            "B": (-1, 0),
            "L": (0, 1),
            "R": (0, -1),
            "S": (0, 0),
        }
        if command in legacy_map:
            linear, angular = legacy_map[command]
            self.send_velocity(linear, angular)
        else:
            self.current_command = command.encode() if isinstance(command, str) else command
            print(f"Updated current command to raw payload: {self.current_command}")
    
    def close(self):
        """Closes the serial port and stops the sending loop."""
        self.running = False
        if self.sending_thread:
            self.sending_thread.join(timeout=1)
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("Serial port closed.")
            else:
                print("Serial port is already closed.")
        except:
            print("Error closing serial port")