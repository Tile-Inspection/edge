from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from hardware.serial import SerialCommunicator

serial_communicator = SerialCommunicator()

class ControlRequest(BaseModel):
    action: str
    direction: str | None = None

router = APIRouter()

@router.post("/control")
def control(request: ControlRequest):
    if request.action == "move":
        if request.direction not in {"forward", "backward", "left", "right"}:
            raise HTTPException(status_code=400, detail="Invalid direction for move action")
        
        if request.direction == "forward":
            serial_communicator.send_command("F")
        elif request.direction == "backward":
            serial_communicator.send_command("B")
        elif request.direction == "left":
            serial_communicator.send_command("L")
        elif request.direction == "right":
            serial_communicator.send_command("R")
    elif request.action == "stop":
        serial_communicator.send_command("S")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    return {"status": "success"}
