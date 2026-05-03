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

router = APIRouter()

@router.post("/control")
def control(request: Request, body: ControlRequest):
    scan_service: ScanService = request.app.state.scan_service
    serial_communicator = scan_service.controller.serial_communicator

    if body.action == "move":
        if body.direction not in {"forward", "backward", "left", "right"}:
            raise HTTPException(status_code=400, detail="Invalid direction for move action")
        
        if body.direction == "forward":
            serial_communicator.send_velocity(1, 0)
        elif body.direction == "backward":
            serial_communicator.send_velocity(-1, 0)
        elif body.direction == "left":
            serial_communicator.send_velocity(0, 1)
        elif body.direction == "right":
            serial_communicator.send_velocity(0, -1)
    elif body.action == "stop":
        serial_communicator.send_velocity(0, 0)
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
