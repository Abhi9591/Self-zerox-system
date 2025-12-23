
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.routes import admin, machine, session, payment, print

# Create tables for simplicity (in prod use migration)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(machine.router, prefix="/api/v1/machine", tags=["machine"])
app.include_router(session.router, prefix="/api/v1/session", tags=["session"])
app.include_router(payment.router, prefix="/api/v1/payment", tags=["payment"])
app.include_router(print.router, prefix="/api/v1/print", tags=["print"])

from app.routes import storage
app.include_router(storage.router, prefix="/api/v1/storage", tags=["storage"])

# Mount Frontend (Kiosk + Mobile)
# Assuming frontend folder is at ../frontend relative to backend
import os
frontend_path = os.path.join(os.path.dirname(__file__), '../../frontend')
if os.path.exists(frontend_path):
    app.mount("/kiosk", StaticFiles(directory=os.path.join(frontend_path, "kiosk"), html=True), name="kiosk")
    app.mount("/mobile", StaticFiles(directory=os.path.join(frontend_path, "mobile"), html=True), name="mobile")
    app.mount("/admin", StaticFiles(directory=os.path.join(frontend_path, "admin"), html=True), name="admin")
    
@app.get("/")
def root():
    return {"message": "Self Xerox Kiosk System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
