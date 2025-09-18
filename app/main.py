"""Main FastAPI application"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import os
import asyncio
from contextlib import asynccontextmanager

from app.database import engine, get_db
from app import models
from app.routers import auth, clients, cases, events, stats

# Create tables
models.Base.metadata.create_all(bind=engine)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="AvukatAjanda API",
    version="2.0.0",
    description="Legal Practice Management System API",
    lifespan=lifespan
)

# CORS configuration
origins = os.getenv("CORS_ORIGIN", "https://avukatajanda.com,http://localhost:3000").split(",")
origins = [origin.strip() for origin in origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AvukatAjanda API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {
        "ok": True,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with database ping"""
    try:
        # Try to connect to database with timeout
        db: Session = next(get_db())
        
        # Execute a simple query with timeout
        async def check_db():
            try:
                db.execute(text("SELECT 1"))
                return True
            except Exception:
                return False
            finally:
                db.close()
        
        # Run with 2 second timeout
        try:
            db_ok = await asyncio.wait_for(check_db(), timeout=2.0)
        except asyncio.TimeoutError:
            db_ok = False
        
        if not db_ok:
            raise HTTPException(
                status_code=503,
                detail={"error": "Database connection failed", "status": "unhealthy"}
            )
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"error": str(e), "status": "unhealthy"}
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error"}
