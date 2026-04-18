from controller.scan_controller import ScanController
from db.crud import create_scan
from db.database import SessionLocal


class ScanService:
    def __init__(self, controller: ScanController):
        self.controller = controller

    def start_scan(self):
        if not self.controller.is_running:
            # Create a new scan record in the database
            db = SessionLocal()
            try:
                scan = create_scan(db, name="New Scan")
                print(f"Scan created with ID: {scan.id}")
            finally:
                db.close()
            
            self.controller.start()

    def stop_scan(self):
        if self.controller.is_running:
            self.controller.stop()