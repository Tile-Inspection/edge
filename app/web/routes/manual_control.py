from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from services.scan_service import ScanService

class ControlRequest(BaseModel):
    action: str
    direction: str | None = None
    speed: str | None = None

router = APIRouter()

@router.post("/control")
def control(request: Request, body: ControlRequest):
    scan_service: ScanService = request.app.state.scan_service
    serial_communicator = scan_service.controller.serial_communicator

    if body.action == "move":
        if body.direction not in {"forward", "backward", "left", "right"}:
            raise HTTPException(status_code=400, detail="Invalid direction for move action")
        
        if body.direction == "forward":
            serial_communicator.send_command("F")
        elif body.direction == "backward":
            serial_communicator.send_command("B")
        elif body.direction == "left":
            serial_communicator.send_command("L")
        elif body.direction == "right":
            serial_communicator.send_command("R")
    elif body.action == "stop":
        serial_communicator.send_command("S")
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
