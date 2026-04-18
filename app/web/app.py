from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from web.routes import scan
from web.routes import health

app = FastAPI(title="Edge Tile Inspection Robot API")

# include API routers
app.include_router(health.router)
app.include_router(scan.router)

app.mount("/", StaticFiles(directory="web/static", html=True), name="static")
