import threading

from controller.scan_controller import ScanController
from db.crud import create_scan
from db.database import SessionLocal


class ScanService:
    def __init__(self, controller: ScanController):
        self.controller = controller
        self.current_scan_id = None

    def start_scan(self, scan_id: int, rows: int, cols: int, tile_size: float):
        if not self.controller.is_running:
            self.current_scan_id = scan_id
            
            # Run the scan sequence in a background thread to prevent blocking API requests
            scan_thread = threading.Thread(
                target=self.controller.start,
                args=(rows, cols, tile_size, scan_id),
                daemon=True
            )
            scan_thread.start()

    def stop_scan(self):
        if self.controller.is_running:
            self.controller.stop()
            self.current_scan_id = None