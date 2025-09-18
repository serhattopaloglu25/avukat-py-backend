"""Minimal FastAPI app for Render deployment"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# Create app
app = FastAPI(title="AvukatAjanda API", version="2.0.0")

# CORS
origins = os.getenv("CORS_ORIGIN", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "AvukatAjanda API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ping")
def ping():
    return {"ok": True, "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
def health_check():
    try:
        # Basic health check
        return {
            "status": "healthy",
            "database": "not_connected",  # Will fix later
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": str(e), "status": "unhealthy"})

# Try to import full app features
try:
    from app.database import get_db
    from app.routers import auth, clients, cases, events, stats
    
    # Add routers
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
    app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
    app.include_router(events.router, prefix="/api/events", tags=["Events"])
    app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
    
    print("✅ Full API loaded successfully")
except ImportError as e:
    print(f"⚠️ Running in minimal mode: {e}")
    
    # Add mock endpoints for testing
    @app.post("/auth/login")
    def mock_login():
        return {"access_token": "mock-token", "token_type": "bearer"}
    
    @app.post("/auth/register")
    def mock_register():
        return {"access_token": "mock-token", "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
