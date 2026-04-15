from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    """Returns current connection status with the Raspberry Pi."""
    return {
        "status": "connected"
    }