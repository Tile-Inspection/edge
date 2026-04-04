# Edge Tile Inspection Robot Backend

Simple modular monolith backend for Raspberry Pi edge robot.

## Structure

- `app/main.py` -- FastAPI entrypoint
- `app/api/routes/*` -- HTTP API route definitions
- `app/core/state.py` -- robot state machine
- `app/services/scan_service.py` -- scanning orchestration
- `app/workers/scan_worker.py` -- simulated scan loop
- `app/db/*` -- SQLAlchemy database boilerplate
- `data/scans/` -- data output path (empty)

## Run

1. `pip install -r requirements.txt`
2. `uvicorn app.main:app --reload`
3. API:
   - `GET /api/status`
   - `POST /api/scan/start`
   - `GET /api/robot`