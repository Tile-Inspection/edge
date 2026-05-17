import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

class WheelEncoder:
    def __init__(self, pin=27, bouncetime=2, vcc_pin=None):
        """
        Initializes a simple wheel encoder.
        :param pin: The BCM GPIO pin number the encoder signal is connected to.
        :param bouncetime: Switch bounce time in milliseconds to prevent double counting.
        :param vcc_pin: Optional BCM GPIO pin number to output HIGH (3.3V) for powering the encoder.
        """
        self.pin = pin
        self.ticks = 0
        self.vcc_pin = vcc_pin
        
        if GPIO_AVAILABLE:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            
            if self.vcc_pin is not None:
                GPIO.setup(self.vcc_pin, GPIO.OUT)
                GPIO.output(self.vcc_pin, GPIO.HIGH)
                print(f"Wheel Encoder VCC powered via GPIO {self.vcc_pin}.")
                
            # Configure pin as an input with an internal pull-up resistor
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # Trigger the callback on both rising and falling edges (can be changed to GPIO.RISING or GPIO.FALLING)
            GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self._tick_callback, bouncetime=bouncetime)
            print(f"Wheel Encoder initialized on GPIO {self.pin}.")
        else:
            print(f"RPi.GPIO not available. Wheel Encoder on pin {self.pin} will be simulated.")

    def _tick_callback(self, channel):
        """Callback function automatically triggered by a hardware interrupt."""
        self.ticks += 1

    def get_ticks(self):
        """Returns the current number of ticks recorded."""
        return self.ticks

    def reset(self):
        """Resets the tick counter to zero."""
        self.ticks = 0