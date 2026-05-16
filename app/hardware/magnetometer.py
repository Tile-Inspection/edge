import math
import time

try:
    import smbus
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False

class Magnetometer:
    """
    Interfaces with a GY-271 (QMC5883L or HMC5883L) magnetometer over I2C.
    Default address is 0x1E (HMC5883L). QMC5883L chips use 0x0D.
    """
    def __init__(self, bus_num=1, address=0x1E):
        self.bus_num = bus_num
        self.address = address
        
        if SMBUS_AVAILABLE:
            try:
                self.bus = smbus.SMBus(self.bus_num)
                self._initialize_sensor()
                time.sleep(0.1)  # Allow sensor to stabilize
                print(f"Magnetometer initialized at I2C address {hex(self.address)}. Initial heading: {self.get_heading():.2f} degrees.")
            except Exception as e:
                print(f"Failed to initialize Magnetometer: {e}")
                self.bus = None
        else:
            self.bus = None
            print("smbus not available. Magnetometer will be simulated.")

    def _initialize_sensor(self):
        """Configures the sensor for continuous measurement mode."""
        if self.bus:
            if self.address == 0x1E:
                # HMC5883L configuration
                self.bus.write_byte_data(self.address, 0x00, 0x70)  # 8-average, 15 Hz default, normal measurement
                self.bus.write_byte_data(self.address, 0x01, 0x20)  # Gain
                self.bus.write_byte_data(self.address, 0x02, 0x00)  # Continuous measurement mode
            else:
                # QMC5883L configuration
                # Control Register 1 (0x09) set to 0x1D: 
                # Continuous measurement, 200Hz data rate, 8G range, 512 Over Sampling Ratio
                self.bus.write_byte_data(self.address, 0x09, 0x1D)

    def _read_word(self, reg, big_endian=False):
        """Reads a 16-bit word from the given register."""
        if big_endian:
            high = self.bus.read_byte_data(self.address, reg)
            low = self.bus.read_byte_data(self.address, reg + 1)
        else:
            low = self.bus.read_byte_data(self.address, reg)
            high = self.bus.read_byte_data(self.address, reg + 1)
            
        val = (high << 8) + low
        
        # Convert to signed 16-bit integer
        if val >= 0x8000:
            return -((65535 - val) + 1)
        return val

    def get_heading(self) -> float:
        """Reads X and Y axis values and calculates the heading in degrees."""
        if not self.bus:
            return 0.0  # Return simulated heading if hardware unavailable

        try:
            if self.address == 0x1E:
                # HMC5883L registers: X_MSB=0x03, Z_MSB=0x05, Y_MSB=0x07 (Big Endian)
                x = self._read_word(0x03, big_endian=True)
                y = self._read_word(0x07, big_endian=True)
            else:
                # QMC5883L registers: X_LSB=0x00, Y_LSB=0x02 (Little Endian)
                x = self._read_word(0x00, big_endian=False)
                y = self._read_word(0x02, big_endian=False)
            
            heading_rad = math.atan2(y, x)
            return (math.degrees(heading_rad) + 360) % 360
        except Exception as e:
            print(f"Error reading magnetometer heading: {e}")
            return 0.0
