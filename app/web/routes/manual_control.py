import threading
import time
import os
import cv2

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from services.scan_service import ScanService
# pyrefly: ignore [missing-import]
from navigation.analyze import read_frame, analyze, Line
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

class Turn90Request(BaseModel):
    direction: str
    
class TileDataRequest(BaseModel):
    tile_id: int
    label: str
    
class RecordVideoRequest(BaseModel):
    duration: float = Field(5.0, gt=0)
    filename: str | None = None

class EncoderTestRequest(BaseModel):
    distance: float = Field(..., gt=0)
    speed: float = Field(0.5, gt=0, le=1)

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

@router.post("/turn-90")
def turn_90(request: Request, body: Turn90Request):
    scan_service: ScanService = request.app.state.scan_service
    navigator = scan_service.controller.navigator
    
    if body.direction == "left":
        navigator.turn_left_90()
    elif body.direction == "right":
        navigator.turn_right_90()
    else:
        raise HTTPException(status_code=400, detail="Invalid direction")
        
    return {"status": "success", "message": f"Turned 90 degrees {body.direction}"}

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

@router.post("/record-video")
def record_video_endpoint(request: Request, body: RecordVideoRequest):
    scan_service: ScanService = request.app.state.scan_service
    
    # Start recording in a background thread to prevent blocking the API
    record_thread = threading.Thread(
        target=scan_service.controller.camera.record_video,
        kwargs={"duration": body.duration, "filename": body.filename}
    )
    record_thread.start()
    
    return {"status": "success", "message": f"Started recording video for {body.duration} seconds"}

@router.post("/test-encoder")
def test_encoder(request: Request, body: EncoderTestRequest):
    scan_service: ScanService = request.app.state.scan_service
    controller = scan_service.controller
    
    # Run the auto-run logic which uses both encoders and keeps the robot straight
    left_ticks, right_ticks = controller.navigator.forward_distance(
        speed=body.speed, 
        distance_meters=body.distance
    )
    
    return {
        "status": "success", 
        "message": f"Encoder test completed. Target: {body.distance}, Left: {left_ticks}, Right: {right_ticks}"
    }

@router.post("/capture-tile-data")
def capture_tile_data(request: Request, body: TileDataRequest):
    scan_service: ScanService = request.app.state.scan_service
    
    base_name = f"tile_{body.tile_id}_{body.label}"
    img_filename = f"{base_name}.jpg"
    aud_filename = f"{base_name}.wav"
    aud_long_filename = f"{base_name}_long.wav"
    
    # Capture the image
    scan_service.controller.camera.capture(img_filename)
    
    # Start recording in a background thread to prevent blocking
    record_thread = threading.Thread(
        target=scan_service.controller.mic.record,
        kwargs={"duration": 1, "filename": aud_filename}
    )
    record_thread.start()
    
    # Wait 200ms (0.2 seconds), then tap the solenoid
    time.sleep(0.2)
    scan_service.controller.solenoid.tap()
    
    # Wait for the 1-second recording to finish before returning the response
    record_thread.join()
    
    # Record long tap
    record_thread = threading.Thread(
        target=scan_service.controller.mic.record,
        kwargs={"duration": 1, "filename": aud_long_filename}
    )
    record_thread.start()
    
    # Wait 200ms (0.2 seconds), then tap the solenoid
    time.sleep(0.2)
    scan_service.controller.solenoid.tap(duration=0.3)
    
    # Wait for the 1-second recording to finish before returning the response
    record_thread.join()
    
    return {
        "status": "success", 
        "message": f"Captured {base_name}.jpg and {base_name}.wav/{base_name}_long.wav"
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
        left_line_interpolated = left_line.extend_line_to_frame(X_DIM, Y_DIM)
    if right_line is not None:
        right_line_interpolated = right_line.extend_line_to_frame(X_DIM, Y_DIM)
    
    if left_line is not None:
        cv2.line(frame, (left_line.x1, left_line.y1), (left_line.x2, left_line.y2), (255, 0, 0), 2)
    if right_line is not None:
        cv2.line(frame, (right_line.x1, right_line.y1), (right_line.x2, right_line.y2), (255, 0, 0), 2)
    
    if left_line_interpolated is not None:
        cv2.line(frame, (left_line_interpolated.x1, left_line_interpolated.y1), (left_line_interpolated.x2, left_line_interpolated.y2), (0, 255, 0), 1)
    if right_line_interpolated is not None:
        cv2.line(frame, (right_line_interpolated.x1, right_line_interpolated.y1), (right_line_interpolated.x2, right_line_interpolated.y2), (0, 255, 0), 1)
        
    save_path = os.path.join(static_dir, "detected.jpg")
    cv2.imwrite(save_path, frame)
    
    return {"status": "success", "filename": "/detected.jpg"}

@router.get("/battery")
def get_battery(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    return {
        "status": "success", 
        "battery": scan_service.controller.serial_communicator.battery
    }
