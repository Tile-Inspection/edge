try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

class PhysicalButtons:
    def __init__(self, pin1=10, pin2=9, pin3=11):
        self.pins = [pin1, pin2, pin3]
        self.buttons = []
        
        if GPIO_AVAILABLE:
            for i, pin in enumerate(self.pins):
                # pull_up=True assumes buttons are wired between the GPIO pin and Ground.
                btn = Button(pin, pull_up=True, bounce_time=0.1)
                btn.when_pressed = self._make_callback(i + 1)
                self.buttons.append(btn)
            print(f"Physical buttons initialized on GPIO pins: {self.pins}")
        else:
            print("gpiozero not available. Physical buttons will not be active.")

    def _make_callback(self, button_num):
        def callback():
            print(f"Button {button_num} clicked")
        return callback