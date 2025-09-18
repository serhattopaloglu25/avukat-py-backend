from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(title="AvukatAjanda API", version="2.0.0")

# CORS
origins = os.getenv("CORS_ORIGIN", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "AvukatAjanda API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/ping")
async def ping():
    return {
        "ok": True,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "testing",
        "version": "2.0.0"
    }

# Import routers after basic setup
try:
    from app.routers import auth, clients, cases, events, stats
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
    app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
    app.include_router(events.router, prefix="/api/events", tags=["Events"])
    app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
    print("✅ All routers loaded successfully")
except Exception as e:
    print(f"⚠️ Could not load routers: {e}")
    print("Running in basic mode")
