import threading
import time
import os
import cv2

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from services.scan_service import ScanService
from navigation.analyze import read_frame, analyze
from constants import X_DIM, Y_DIM

class ControlRequest(BaseModel):
    action: str
    direction: str | None = None
    speed: str | None = None

class VelocityRequest(BaseModel):
    linear: float = Field(..., ge=-1, le=1)  # Linear velocity (-1 to 1) - positive = forward, negative = backward
    angular: float = Field(..., ge=-1, le=1)  # Angular velocity (-1 to 1) - positive = turn left, negative = turn right
    
class TestMoveRequest(BaseModel):
    direction: str
    speed: float = Field(..., ge=0, le=1)
    duration: float = Field(..., gt=0)
    
class TileDataRequest(BaseModel):
    tile_id: int
    label: str

router = APIRouter()

@router.post("/control")
def control(request: Request, body: ControlRequest):
    scan_service: ScanService = request.app.state.scan_service
    navigator = scan_service.controller.navigator

    if body.action == "move":
        if body.direction not in {"forward", "backward", "left", "right"}:
            raise HTTPException(status_code=400, detail="Invalid direction for move action")
        
        if body.direction == "forward":
            navigator.move_forward_tile()
        elif body.direction == "backward":
            navigator.move_backward_tile()
        elif body.direction == "left":
            navigator.turn_left()
        elif body.direction == "right":
            navigator.turn_right()
    elif body.action == "stop":
        navigator.motion.stop()
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    return {"status": "success"}

@router.post("/test-move")
def test_move(request: Request, body: TestMoveRequest):
    scan_service: ScanService = request.app.state.scan_service
    navigator = scan_service.controller.navigator

    if body.direction == "forward":
        navigator.forward(body.speed, body.duration)
    elif body.direction == "right":
        navigator.right(body.speed, body.duration)
    elif body.direction == "left":
        navigator.left(body.speed, body.duration)
    else:
        raise HTTPException(status_code=400, detail="Invalid direction")
        
    return {"status": "success", "message": f"Moved {body.direction}"}

@router.post("/capture")
def capture(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    filename = scan_service.controller.camera.capture()
    return {"filename": filename}

@router.post("/record")
def record_audio(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    # Records 1 second of audio and saves it as sound.wav
    filename = scan_service.controller.mic.record(duration=1, filename="sound.wav")
    return {"filename": filename}

@router.post("/capture-tile-data")
def capture_tile_data(request: Request, body: TileDataRequest):
    scan_service: ScanService = request.app.state.scan_service
    
    base_name = f"tile_{body.tile_id}_{body.label}"
    img_filename = f"{base_name}.jpg"
    aud_filename = f"{base_name}.wav"
    
    # Capture the image
    scan_service.controller.camera.capture(img_filename)
    
    # Start recording in a background thread to prevent blocking
    record_thread = threading.Thread(
        target=scan_service.controller.mic.record,
        kwargs={"duration": 0.3, "filename": aud_filename}
    )
    record_thread.start()
    
    # Wait 50ms (0.05 seconds), then tap the solenoid
    time.sleep(0.05)
    scan_service.controller.solenoid.tap()
    
    # Wait for the 1-second recording to finish before returning the response
    record_thread.join()
    
    return {
        "status": "success", 
        "message": f"Captured {base_name}.jpg and {base_name}.wav"
    }

@router.post("/velocity")
def set_velocity(request: Request, command: VelocityRequest):
    scan_service: ScanService = request.app.state.scan_service
    motion = scan_service.controller.motion
    motion.send_velocity(command.linear, command.angular)
    return {"status": "success", "linear": command.linear, "angular": command.angular}

@router.post("/solenoid")
def set_solenoid(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    solenoid = scan_service.controller.solenoid
    solenoid.tap()
    return {"status": "success", "message": "Solenoid activated"}

@router.post("/spray")
def set_spray(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    sprayer = scan_service.controller.sprayer
    sprayer.spray()
    return {"status": "success", "message": "Spray activated"}

@router.post("/test-vision")
def test_vision(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    camera = scan_service.controller.camera
    
    filename = camera.capture()
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    
    if not filename or not os.path.exists(filename):
        filename = os.path.join(static_dir, "sample.jpg")
        
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Image not found for processing")
        
    frame = read_frame(filename, x_dim=X_DIM, y_dim=Y_DIM)
    _, _, left_line, right_line = analyze(frame, x_dim=X_DIM, y_dim=Y_DIM)
    
    if left_line is not None:
        cv2.line(frame, (left_line.x1, left_line.y1), (left_line.x2, left_line.y2), (255, 0, 0), 2)
    if right_line is not None:
        cv2.line(frame, (right_line.x1, right_line.y1), (right_line.x2, right_line.y2), (255, 0, 0), 2)
        
    save_path = os.path.join(static_dir, "detected.jpg")
    cv2.imwrite(save_path, frame)
    
    return {"status": "success", "filename": "/detected.jpg"}
