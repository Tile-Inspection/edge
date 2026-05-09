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

class BatteryRequest(BaseModel):
    battery: float = Field(..., ge=6.0, le=8.4)  # Battery level (6.0 to 8.4)

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

@router.post("/battery")
def set_battery(request: Request, command: BatteryRequest):
    scan_service: ScanService = request.app.state.scan_service
    serial_communicator = scan_service.controller.serial_communicator
    serial_communicator.send_battery(command.battery)
    return {"status": "success", "battery": command.battery}

@router.get("/measure_battery")
def get_battery(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    adc = scan_service.controller.adc
    battery_voltage = adc.read_voltage() * 147 / 47
    return {"status": "success", "battery": battery_voltage}

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
