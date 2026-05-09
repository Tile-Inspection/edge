try:
    import board
    import busio
    from adafruit_ads1x15.analog_in import AnalogIn
    from adafruit_ads1x15 import ads1x15 as adsx, ADS1115
    ADC_AVAILABLE = True
except ImportError:
    ADC_AVAILABLE = False

class ADC:
    def __init__(self, channel=0):
        self.channel = channel
        if ADC_AVAILABLE:
            # Initialize the I2C interface (SCL and SDA pins)
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS1115(self.i2c)
            # Map the integer channel (0-3) to the ADS pin
            pins = [adsx.Pin.A0, adsx.Pin.A1, adsx.Pin.A2, adsx.Pin.A3]
            self.chan = AnalogIn(self.ads, pins[self.channel])
            print(f"ADS1115 initialized on channel {self.channel}.")
        else:
            print(f"ADS1x15 libraries not found. ADC channel {self.channel} will be simulated.")

    def read_voltage(self):
        if ADC_AVAILABLE:
            return self.chan.voltage
        else:
            # Return a simulated nominal 2S LiPo battery voltage for local development
            print(f"Returning simulated voltage for ADC channel {self.channel}.")
            return 7.4