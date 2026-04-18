from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from web.routes import scan
from web.routes import health

app = FastAPI(title="Edge Tile Inspection Robot API")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include API routers
app.include_router(health.router)
app.include_router(scan.router)

app.mount("/", StaticFiles(directory="web/static", html=True), name="static")
