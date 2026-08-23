from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.database import Base, engine
from backend.seed_loader import load_seed
from backend.routers import roles, compare, rank

app = FastAPI(
    title="Role-Level AI Intelligence",
    description="Analyses the future AI impact (automation/augmentation) of enterprise roles, "
                 "with full explainability of every conclusion.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roles.router)
app.include_router(compare.router)
app.include_router(rank.router)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    load_seed(reset=False)


@app.get("/api/health")
def health():
    return {"status": "ok"}
