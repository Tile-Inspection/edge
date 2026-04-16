from controller.scan_controller import ScanController


class ScanService:
    def __init__(self, controller: ScanController):
        self.controller = controller

    def start_scan(self):
        if not self.controller.is_running:
            self.controller.start()

    def stop_scan(self):
        if self.controller.is_running:
            self.controller.stop()