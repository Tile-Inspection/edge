import math
import time
import json
import os

try:
    import smbus
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False

CALIBRATION_FILE = os.path.join(os.path.dirname(__file__), "magnetometer_cal.json")

class Magnetometer:
    """
    Interfaces with a GY-271 (QMC5883L or HMC5883L) magnetometer over I2C.
    Default address is 0x1E (HMC5883L). QMC5883L chips use 0x0D.
    """
    def __init__(self, bus_num=1, address=0x1E, offset_x=-15, offset_y=31.5, scale_x=1.0503, scale_y=0.9543, declination_rad=math.radians (-2.57)):
        self.bus_num = bus_num
        self.address = address
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.declination_rad = declination_rad
        
        self._load_calibration()
        
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

    def _load_calibration(self):
        """Loads offset and scale values from a local file if it exists."""
        if os.path.exists(CALIBRATION_FILE):
            try:
                with open(CALIBRATION_FILE, 'r') as f:
                    data = json.load(f)
                    self.offset_x = data.get('offset_x', self.offset_x)
                    self.offset_y = data.get('offset_y', self.offset_y)
                    self.scale_x = data.get('scale_x', self.scale_x)
                    self.scale_y = data.get('scale_y', self.scale_y)
                print("Loaded magnetometer calibration data.")
            except Exception as e:
                print(f"Failed to load calibration data: {e}")
                
    def _save_calibration(self):
        """Saves current offset and scale values to a local file."""
        data = {
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'scale_x': self.scale_x,
            'scale_y': self.scale_y
        }
        try:
            with open(CALIBRATION_FILE, 'w') as f:
                json.dump(data, f)
            print("Saved magnetometer calibration data.")
        except Exception as e:
            print(f"Failed to save calibration data: {e}")

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

    def _get_raw_xy(self):
        """Reads raw, uncalibrated X and Y axis values from the sensor."""
        if not self.bus:
            return 0, 0
            
        try:
            if self.address == 0x1E:
                data = self.bus.read_i2c_block_data(self.address, 0x03, 6)
                x = (data[0] << 8) | data[1]
                y = (data[4] << 8) | data[5]
            else:
                data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
                x = (data[1] << 8) | data[0]
                y = (data[3] << 8) | data[2]
            
            # Convert unsigned 16-bit values to signed 16-bit integers
            x = x - 65536 if x >= 32768 else x
            y = y - 65536 if y >= 32768 else y
            return x, y
        except Exception as e:
            print(f"Error reading raw magnetometer data: {e}")
            return 0, 0

    def get_heading(self) -> float:
        """Reads X and Y axis values and calculates the heading in degrees."""
        if not self.bus:
            return 0.0  # Return simulated heading if hardware unavailable

        try:
            x, y = self._get_raw_xy()

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
            
    def calibrate(self, motion_controller, duration=15.0, spin_speed=0.5):
        """
        Spins the robot in place to collect min and max readings for X and Y,
        calculates hard and soft iron offsets, and saves them locally.
        """
        if not self.bus:
            print("Cannot calibrate: Magnetometer hardware is not available.")
            return
            
        print(f"Starting magnetometer calibration for {duration} seconds. Ensure area is clear...")
        motion_controller.turn_right(spin_speed)
        
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        
        start_time = time.time()
        while time.time() - start_time < duration:
            x, y = self._get_raw_xy()
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            time.sleep(0.05)
            
        motion_controller.stop()
        
        # Calculate Hard Iron offsets (Center of the sphere/ellipse)
        self.offset_x = (max_x + min_x) / 2
        self.offset_y = (max_y + min_y) / 2
        
        # Calculate Soft Iron scale (Rescaling the ellipse into a circle)
        avg_delta_x = (max_x - min_x) / 2
        avg_delta_y = (max_y - min_y) / 2
        avg_delta = (avg_delta_x + avg_delta_y) / 2
        
        self.scale_x = avg_delta / avg_delta_x if avg_delta_x != 0 else 1.0
        self.scale_y = avg_delta / avg_delta_y if avg_delta_y != 0 else 1.0
        
        print(f"Calibration complete. Offsets: x={self.offset_x:.2f}, y={self.offset_y:.2f}")
        print(f"Scales: x={self.scale_x:.4f}, y={self.scale_y:.4f}")
        
        self._save_calibration()
