import time
import threading

try:
    import smbus
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False

class MPU6050:
    def __init__(self, bus_num=1, address=0x68):
        self.bus_num = bus_num
        self.address = address
        
        self.gyro_z_offset = 0.0
        self.heading = 0.0
        
        self.running = False
        
        if SMBUS_AVAILABLE:
            try:
                self.bus = smbus.SMBus(self.bus_num)
                self._initialize_sensor()
                self._calibrate_gyro()
                
                self.running = True
                self.last_time = time.time()
                self.thread = threading.Thread(target=self._update_loop, daemon=True)
                self.thread.start()
                
                print(f"MPU6050 initialized at I2C address {hex(self.address)}.")
            except Exception as e:
                print(f"Failed to initialize MPU6050: {e}")
                self.bus = None
        else:
            self.bus = None
            print("smbus not available. MPU6050 will be simulated.")

    def _initialize_sensor(self):
        # Wake up MPU6050 (write 0 to power management register 1)
        self.bus.write_byte_data(self.address, 0x6B, 0x00)
        # Set gyro config to +/- 250 degrees/sec
        self.bus.write_byte_data(self.address, 0x1B, 0x00)

    def _read_raw_data(self, addr):
        try:
            high = self.bus.read_byte_data(self.address, addr)
            low = self.bus.read_byte_data(self.address, addr+1)
            value = ((high << 8) | low)
            if value > 32768:
                value = value - 65536
            return value
        except Exception:
            return 0

    def _calibrate_gyro(self):
        print("Calibrating MPU6050 gyro. Please keep the robot still...")
        num_samples = 200
        z_sum = 0
        for _ in range(num_samples):
            z_sum += self._read_raw_data(0x47) # Gyro Z register
            time.sleep(0.01)
        self.gyro_z_offset = z_sum / num_samples
        print(f"Gyro Z offset: {self.gyro_z_offset:.2f}")

    def _update_loop(self):
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time
            
            raw_z = self._read_raw_data(0x47)
            gz = (raw_z - self.gyro_z_offset) / 131.0
            
            # Deadband to prevent drift from minor noise
            if abs(gz) > 1.0:
                self.heading += gz * dt
                
            time.sleep(0.01)

    def get_heading(self):
        if not self.bus:
            return 0.0
        return self.heading
        
    def reset_heading(self):
        self.heading = 0.0

    def close(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()