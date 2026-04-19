from controller.scan_controller import ScanController
from db.crud import create_scan
from db.database import SessionLocal


class ScanService:
    def __init__(self, controller: ScanController):
        self.controller = controller
        self.current_scan_id = None

    def start_scan(self, scan_id: int):
        if not self.controller.is_running:
            self.current_scan_id = scan_id
            self.controller.start()

    def stop_scan(self):
        if self.controller.is_running:
            self.controller.stop()
            self.current_scan_id = None