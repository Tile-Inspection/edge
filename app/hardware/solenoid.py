import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

class Solenoid:
    def __init__(self, pin=18):
        self.pin = pin
        if GPIO_AVAILABLE:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.HIGH)
            print(f"Solenoid initialized on GPIO {self.pin}.")
        else:
            print("RPi.GPIO not available. Solenoid functionality will be simulated.")

    def tap(self, duration=0.5):
        if GPIO_AVAILABLE:
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(duration)
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            print(f"Simulated solenoid tap on pin {self.pin} for {duration} seconds.")