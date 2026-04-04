from fastapi import FastAPI
from app.api.routes import health, scan

app = FastAPI(title="Edge Tile Inspection Robot API")

# include API routers
app.include_router(health.router)
app.include_router(scan.router)
