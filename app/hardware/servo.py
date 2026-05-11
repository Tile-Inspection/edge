import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

class SprayerServo:
    def __init__(self, pin=22):
        self.pin = pin
        if GPIO_AVAILABLE:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            # MG996R typically operates at 50Hz
            self.pwm = GPIO.PWM(self.pin, 50)
            self.pwm.start(0)  # Start with 0 duty cycle (no active signal to prevent jitter)
            print(f"Sprayer Servo initialized on GPIO {self.pin}.")
        else:
            print(f"RPi.GPIO not available. Sprayer Servo on pin {self.pin} will be simulated.")

    def spray(self):
        """Actuates the servo to push the nozzle and then retracts."""
        if GPIO_AVAILABLE:
            # Duty cycle 12.5 is typically ~180 degrees. (Adjust based on your mount!)
            self.pwm.ChangeDutyCycle(12.5)
            time.sleep(0.5)  # Wait for the servo to reach the position
            
            # Duty cycle 2.5 is typically ~0 degrees (Resting position).
            self.pwm.ChangeDutyCycle(2.5)
            time.sleep(0.5)
            self.pwm.ChangeDutyCycle(0)  # Stop sending PWM to prevent servo jitter
        else:
            print(f"Simulated spray actuation on GPIO {self.pin}.")
