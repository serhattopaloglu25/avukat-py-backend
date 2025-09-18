from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AvukatAjanda API", "version": "2.0"}

@app.get("/ping")
def ping():
    return {"ok": True, "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
