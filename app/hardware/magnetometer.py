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
    def __init__(self, bus_num=1, address=0x1E, offset_x=-11.0, offset_y=192.5, scale_x=1.0287, scale_y=0.9729, declination_rad=0.0):
        self.bus_num = bus_num
        self.address = address
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.declination_rad = declination_rad
        
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

    def get_heading(self) -> float:
        """Reads X and Y axis values and calculates the heading in degrees."""
        if not self.bus:
            return 0.0  # Return simulated heading if hardware unavailable

        try:
            if self.address == 0x1E:
                # HMC5883L registers: X_MSB=0x03 to Y_LSB=0x08 (Big Endian)
                # You MUST read all 6 bytes sequentially to unlock the data registers for the next reading.
                data = self.bus.read_i2c_block_data(self.address, 0x03, 6)
                x = (data[0] << 8) | data[1]
                y = (data[4] << 8) | data[5]
            else:
                # QMC5883L registers: X_LSB=0x00 to Z_MSB=0x05 (Little Endian)
                data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
                x = (data[1] << 8) | data[0]
                y = (data[3] << 8) | data[2]
            
            # Convert unsigned 16-bit values to signed 16-bit integers
            x = x - 65536 if x >= 32768 else x
            y = y - 65536 if y >= 32768 else y

            # Apply Hard Iron Offset (Shift to center)
            shifted_x = x - self.offset_x
            shifted_y = y - self.offset_y

            # Apply Soft Iron Scale (Fix the ellipse)
            cal_x = shifted_x * self.scale_x
            cal_y = shifted_y * self.scale_y

            # Calculate Heading and Correct for True North
            heading_rad = math.atan2(cal_y, cal_x) + self.declination_rad

            # Normalize the angle to 0 - 360 degrees
            if heading_rad < 0:
                heading_rad += 2 * math.pi
            elif heading_rad > 2 * math.pi:
                heading_rad -= 2 * math.pi

            return math.degrees(heading_rad)
        except Exception as e:
            print(f"Error reading magnetometer heading: {e}")
            return 0.0
