class ScanController:
    def __init__(self):
        self.init = False
        self.is_running = False

    def start(self):
        self.is_running = True

    def run(self):
        if (not self.init):
            self.init = True
            print("ScanController is running...")
        while True:
            if self.is_running:
                # Perform scanning operations here
                pass