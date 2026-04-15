from fastapi import FastAPI
from web.routes import scan
from web.routes import health

app = FastAPI(title="Edge Tile Inspection Robot API")

# include API routers
app.include_router(health.router)
app.include_router(scan.router)
