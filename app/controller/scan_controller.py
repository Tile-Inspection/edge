class ScanController:
    def __init__(self):
        self.init = False
        self.is_running = False
        print("ScanController is stopping...")

    def start(self):
        self.is_running = True
        print("ScanController is running...")

    def stop(self):
        self.is_running = False
        print("ScanController is stopped...")

    def run(self):
        if (not self.init):
            self.init = True
            print("ScanController is initiated...")
        while True:
            if self.is_running:
                # Perform scanning operations here
                pass