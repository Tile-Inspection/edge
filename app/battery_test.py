import argparse
from threading import Thread
import threading
import time
import uvicorn
from web.app import app as web_app
from services.scan_service import ScanService
from controller.scan_controller import ScanController

parser = argparse.ArgumentParser(description="Battery test")

controller = ScanController(enable_audio=False, enable_crack=False, enable_grout_correction=False)
scan_service = ScanService(controller)

web_app.state.scan_service = scan_service

def start_web():
    uvicorn.run("web.app:app", host="0.0.0.0", port=8000)
    
    
def _temp_inspect():
    # Filenames are relative to the static dir for serving via the web server.
    base_name = f"battery_test"
    img_filename = f"{base_name}.jpg"
    aud_filename = f"{base_name}.wav"
    
    record_thread = threading.Thread(
        target=controller.mic.record,
        kwargs={"duration": 1, "filename": aud_filename}
    )
    record_thread.start()
    
    # Wait 300ms (0.3 seconds), then tap the solenoid while recording
    time.sleep(0.3)
    controller.solenoid.tap()
    
    # Wait for the recording to finish, then classify
    record_thread.join()
    
    # These methods save files and return the full path.
    image_path = controller.camera.capture(filename=img_filename)

    print(f"Captured {image_path} and audio")
    

if __name__ == "__main__":
    try:
        # Start web server in background
        Thread(target=start_web, daemon=True).start()
        
        # Give Uvicorn a moment to initialize before potentially blocking the main thread
        time.sleep(1)
        
        while True:
            controller.navigator.forward_distance(speed=0.3, distance_meters=0.3)
            time.sleep(0.5)
            _temp_inspect()
            
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        controller.serial_communicator.close()
        controller.camera.close()
    