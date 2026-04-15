from threading import Thread
import time
import uvicorn
from controller.scan_controller import ScanController

controller = ScanController()

def start_web():
    uvicorn.run("web.app:app", host="127.0.0.1", port=8000)

if __name__ == "__main__":
    # Start web server in background
    Thread(target=start_web, daemon=True).start()
    
    # Give Uvicorn a moment to initialize before potentially blocking the main thread
    time.sleep(1)
    
    controller.run()