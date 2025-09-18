from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import engine, Base
from app.routers import auth, clients, cases, events, stats

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown

app = FastAPI(
    title="AvukatAjanda API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
origins = os.getenv("CORS_ORIGIN", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health checks
@app.get("/ping")
async def ping():
    return {"ok": True}

@app.get("/health")
async def health():
    try:
        # DB check with timeout
        from app.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "db": "disconnected", "error": str(e)}
        )

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(stats.router, prefix="/api", tags=["stats"])

@app.get("/")
async def root():
    return {"message": "AvukatAjanda API v1.0"}
