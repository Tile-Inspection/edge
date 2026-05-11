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
        
        self._current_command = None
        self.sending_thread = None
        self.running = False
        self.start_sending_loop()
        
    def set_command(self, command: str):
        """Sets the current command to be sent to the serial device."""
        self._current_command = command
    
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
        if self.ser and self.ser.is_open and self._current_command:
            if isinstance(self._current_command, str):
                payload = self._current_command.encode()
            else:
                payload = self._current_command
            self.ser.write(payload)
    
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