from fastapi import APIRouter, Request, HTTPException

from services.scan_service import ScanService
from db.database import get_db
from db.crud import get_all_scans, get_scan_results, get_result

router = APIRouter()

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
    
@router.post("/start-scan")
def start_scan(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    scan_service.start_scan()
    return {"status": "started"}
    
@router.post("/stop-scan")
def stop_scan(request: Request):
    scan_service: ScanService = request.app.state.scan_service
    scan_service.stop_scan()
    return {"status": "stopped"}
