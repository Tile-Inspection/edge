from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from services.scan_service import ScanService
from db.database import get_db
from db.crud import get_all_scans, get_scan_results, get_result, create_scan

class CreateScanRequest(BaseModel):
    name: str
    
class StartScanRequest(BaseModel):
    scanId: int
    tileSize: float = Field(0.3, gt=0)  # Tile size in meters (e.g., 0.3 for 30cm)
    rows: int = Field(3, gt=0)  # Number of rows to scan
    cols: int = Field(2, gt=0)  # Number of cols to scan

router = APIRouter()

@router.get("/status")
def getStatus(request: Request):
    """Fetches the current status of the scanning process."""
    scan_service: ScanService = request.app.state.scan_service
    return {
        "is_running": scan_service.controller.is_running,
        "current_scan_id": scan_service.current_scan_id
    }


@router.get("/scans")
def getScans():
    """Fetches all available scan sessions."""
    with get_db() as db:
        scans = get_all_scans(db)
        return [
            {"id": scan.id, "name": scan.name, "date": scan.time.isoformat()} for scan in scans
        ]

@router.get("/scans/{scanId}/results")
def getResults(scanId: int):
    """Fetches all tile results for a specific scan."""
    with get_db() as db:
        results = get_scan_results(db, scanId)
        return [
            {
                "scanId": result.scan_id,
                "id": result.id,
                "x": result.x,
                "y": result.y,
                "status": result.status,
                "hollowClassification": result.hollow_classification,
                "crackedClassification": result.cracked_classification,
                "imageFilePath": result.image_file_path,
                "audioFilePath": result.audio_file_path,
            }
            for result in results
        ]

@router.get("/grid/{gridId}")
def getGrid(gridId: int):
    """Fetches a single tile/grid item."""
    with get_db() as db:
        result = get_result(db, gridId)
        if not result:
            raise HTTPException(status_code=404, detail="Grid item not found")
        return {
            "scanId": result.scan_id,
            "id": result.id,
            "x": result.x,
            "y": result.y,
            "status": result.status,
            "hollowClassification": result.hollow_classification,
            "crackedClassification": result.cracked_classification,
            "imageFilePath": result.image_file_path,
            "audioFilePath": result.audio_file_path,
        }
    
@router.post("/create-scan")
def createScan(request: CreateScanRequest):
    """Creates a new scan session."""
    with get_db() as db:
        scan = create_scan(db, request.name)
        return {"id": scan.id, "name": scan.name, "date": scan.time.isoformat()}
    
@router.post("/start-scan")
def startScan(request: Request, body: StartScanRequest):
    scan_service: ScanService = request.app.state.scan_service
    scan_service.start_scan(body.scanId, rows=body.rows, cols=body.cols, tile_size=body.tileSize)
    return {"status": "started"}
    
@router.post("/stop-scan")
def stopScan(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    scan_service.stop_scan()
    return {"status": "stopped"}
