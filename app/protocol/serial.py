import serial
import threading
import time
import re

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
        self.receiving_thread = None
        self.battery = None
        self.running = False
        self.start_loops()
        
    def set_command(self, command: str):
        """Sets the current command to be sent to the serial device."""
        self._current_command = command
    
    def start_loops(self):
        """Starts background threads for sending and receiving data."""
        if self.ser and not self.running:
            self.running = True
            self.sending_thread = threading.Thread(target=self._send_loop, daemon=True)
            self.receiving_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.sending_thread.start()
            self.receiving_thread.start()
    
    def _send_loop(self):
        """Internal loop that sends the current command every 100ms."""
        while self.running:
            self._send_current_command()
            time.sleep(0.1)  # 10Hz = 0.1 seconds
    
    def _receive_loop(self):
        """Internal loop that reads incoming data from the serial device."""
        buffer = ""
        while self.running:
            if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
                try:
                    data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                    for char in data:
                        if char == '<':
                            buffer = ""
                        elif char == '>':
                            self._process_payload(buffer)
                            buffer = ""
                        else:
                            buffer += char
                except Exception as e:
                    print(f"Error reading serial data: {e}")
            else:
                time.sleep(0.01)
                
    def _process_payload(self, payload: str):
        """Processes a complete payload received from the serial device."""
        payload_lower = payload.lower()
        if payload_lower.startswith("battery"):
            match = re.search(r"[-+]?\d*\.\d+|\d+", payload_lower)
            if match:
                self.battery = float(match.group())

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
        if self.receiving_thread:
            self.receiving_thread.join(timeout=1)
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("Serial port closed.")
            else:
                print("Serial port is already closed.")
        except:
            print("Error closing serial port")