from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

from app.database import engine, Base, SessionLocal
from app.routers import auth, clients, cases, events, stats
from app.deps import get_current_user

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown

app = FastAPI(
    title="AvukatAjanda API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
cors_origins = os.getenv("CORS_ORIGIN", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health checks
@app.get("/ping")
async def ping():
    return {"ok": True, "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health():
    try:
        # DB check with timeout
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "db": "disconnected", "error": str(e)}
        )

# Me endpoint
@app.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "org_id": getattr(current_user, 'current_org_id', None),
        "role": getattr(current_user, 'role', None)
    }

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(stats.router, prefix="/api", tags=["stats"])

@app.get("/")
async def root():
    return {"message": "AvukatAjanda API v2.0", "status": "running"}
