from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers import attacks, trends, websocket
from services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_scheduler()
    yield
    await stop_scheduler()


app = FastAPI(
    title="Live DDoS Attack Map API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attacks.router, prefix="/api/attacks", tags=["Attacks"])
app.include_router(trends.router, prefix="/api/trends", tags=["Trends"])
app.include_router(websocket.router, tags=["WebSocket"])


@app.get("/")
async def root():
    return {"status": "DDoS Map API running"}


@app.get("/health")
async def health():
    return {"status": "ok"}