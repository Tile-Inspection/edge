import time

try:
    from gpiozero import DigitalInputDevice, OutputDevice
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
            if self.vcc_pin is not None:
                self._vcc = OutputDevice(self.vcc_pin)
                self._vcc.on()
                print(f"Wheel Encoder VCC powered via GPIO {self.vcc_pin}.")
                
            # gpiozero uses seconds for bounce_time; pull_up=True enables internal pull-up resistor
            self._encoder = DigitalInputDevice(self.pin, pull_up=True, bounce_time=bouncetime / 1000.0)
            self._encoder.when_activated = self._tick_callback
            self._encoder.when_deactivated = self._tick_callback
            print(f"Wheel Encoder initialized on GPIO {self.pin}.")
        else:
            print(f"RPi.GPIO not available. Wheel Encoder on pin {self.pin} will be simulated.")

    def _tick_callback(self):
        """Callback function automatically triggered by a hardware interrupt."""
        self.ticks += 1

    def get_ticks(self):
        """Returns the current number of ticks recorded."""
        return self.ticks

    def reset(self):
        """Resets the tick counter to zero."""
        self.ticks = 0