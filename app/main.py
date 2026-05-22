import argparse
from threading import Thread
import time
import uvicorn
from web.app import app as web_app
from services.scan_service import ScanService
from controller.scan_controller import ScanController

parser = argparse.ArgumentParser(description="Edge App")
parser.add_argument("-audio", action="store_true", help="Enable audio classification")
parser.add_argument("-crack", action="store_true", help="Enable crack classification")
args, _ = parser.parse_known_args()

controller = ScanController(enable_audio=args.audio, enable_crack=args.crack)
scan_service = ScanService(controller)

web_app.state.scan_service = scan_service

def start_web():
    uvicorn.run("web.app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    try:
        # Start web server in background
        Thread(target=start_web, daemon=True).start()
        
        # Give Uvicorn a moment to initialize before potentially blocking the main thread
        time.sleep(1)
        
        while True:
            # if controller.is_running:
            #     controller.step()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        controller.serial_communicator.close()
        controller.camera.close()
    