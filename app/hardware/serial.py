import serial

class SerialCommunicator:
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/serial0',
            baudrate=74880,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
    
    def send_command(self, command: str):
        """Sends a command string to the serial device."""
        if self.ser.is_open:
            self.ser.write(command.encode())
            print(f"Sent command: {command}")
        else:
            print("Serial port is not open. Cannot send command.")

    def close(self):
        """Closes the serial port."""
        if self.ser.is_open:
            self.ser.close()
            print("Serial port closed.")
        else:
            print("Serial port is already closed.")