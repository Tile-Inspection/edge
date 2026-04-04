from fastapi import APIRouter

router = APIRouter()

@router.get("/scans")
def getScans():
    """Fetches all available scan sessions."""
    return [
        {"id": 1, "name": "Room 1", "date": "2026-04-02T08:00:00Z"},
        {"id": 2, "name": "Room 2", "date": "2026-04-02T14:30:00Z"}
    ]

@router.get("/scans/{scanId}/results")
def getResults(scanId: int):
    """Fetches all tile results for a specific scan."""
    return [
        {"scanId": scanId, "id": 101, "x": 0, "y": 0, "status": "scanned", "hollowClassification": {"type": "hollow", "confidence": 0.8}, "crackedClassification": None, "imageFilePath": "/path/to/image.jpg", "audioFilePath": "/path/to/audio.mp3"},
        {"scanId": scanId, "id": 102, "x": 1, "y": 0, "status": "scanned", "hollowClassification": {"type": "hollow", "confidence": 0.8}, "crackedClassification": {"type": "cracked", "confidence": 0.9}, "imageFilePath": "/path/to/image.jpg", "audioFilePath": "/path/to/audio.mp3"},
        {"scanId": scanId, "id": 103, "x": 0, "y": 1, "status": "scanned", "hollowClassification": {"type": "hollow", "confidence": 0.7}, "crackedClassification": None, "imageFilePath": "/path/to/image.jpg", "audioFilePath": "/path/to/audio.mp3"}
    ]

@router.get("/grid/{gridId}")
def getGrid(gridId: int):
    """Fetches a single tile/grid item."""
    return {
        "scanId": 1,
        "id": gridId,
        "x": 0,
        "y": 0,
        "status": "scanned",
        "hollowClassification": {"type": "hollow", "confidence": 0.8},
        "crackedClassification": None,
        "imageFilePath": "/path/to/image.jpg",
        "audioFilePath": "/path/to/audio.mp3"
    }
