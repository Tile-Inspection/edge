from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from services.scan_service import ScanService

class ControlRequest(BaseModel):
    action: str
    direction: str | None = None
    speed: str | None = None

class VelocityRequest(BaseModel):
    linear: float  # Linear velocity (m/s) - positive = forward, negative = backward
    angular: float  # Angular velocity (rad/s) - positive = turn left, negative = turn right

router = APIRouter()

@router.post("/control")
def control(request: Request, body: ControlRequest):
    scan_service: ScanService = request.app.state.scan_service
    serial_communicator = scan_service.controller.serial_communicator

    if body.action == "move":
        if body.direction not in {"forward", "backward", "left", "right"}:
            raise HTTPException(status_code=400, detail="Invalid direction for move action")
        
        if body.direction == "forward":
            serial_communicator.send_velocity(100, 0)
        elif body.direction == "backward":
            serial_communicator.send_velocity(-100, 0)
        elif body.direction == "left":
            serial_communicator.send_velocity(0, 50)
        elif body.direction == "right":
            serial_communicator.send_velocity(0, -50)
    elif body.action == "stop":
        serial_communicator.send_velocity(0, 0)
    elif body.action == "speed":
        if body.speed not in {"100", "150", "200"}:
            raise HTTPException(status_code=400, detail="Invalid speed")
        
        if body.speed == "100":
            serial_communicator.send_command("Z")
        elif body.speed == "150":
            serial_communicator.send_command("X")
        elif body.speed == "200":
            serial_communicator.send_command("C")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    return {"status": "success"}

@router.post("/capture")
def capture(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    filename = scan_service.controller.camera.capture()
    return {"filename": filename}

@router.post("/velocity")
def set_velocity(request: Request, command: VelocityRequest):
    scan_service: ScanService = request.app.state.scan_service
    serial_communicator = scan_service.controller.serial_communicator
    serial_communicator.send_velocity(command.linear, command.angular)
    return {"status": "success", "linear": command.linear, "angular": command.angular}
