from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from services.scan_service import ScanService

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
