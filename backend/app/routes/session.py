
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.services import session_service, storage_service
from app.schemas.session import SessionCreate, SessionResponse
from app.utils.qr import generate_qr_base64

router = APIRouter()

@router.post("/", response_model=SessionResponse)
def create_session(
    session_in: SessionCreate,
    db: Session = Depends(deps.get_db)
):
    session = session_service.create_session(db, session_in.machine_id)
    # Generate Upload QR
    # URL structure: http://MOBILE_HOST:8000/mobile/upload.html?session_id=...
    from app.core.config import settings
    upload_url = f"http://{settings.HOST_IP}:{settings.PORT}/mobile/upload.html?session_id={session.session_id}"
    session.upload_url = generate_qr_base64(upload_url)
    return session

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(deps.get_db)):
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/{session_id}/upload-url")
def get_upload_url(session_id: str, filename: str, db: Session = Depends(deps.get_db)):
    # Generate presigned URL for upload
    file_key = f"{session_id}/{filename}"
    url = storage_service.storage_service.generate_presigned_url(file_key)
    if not url:
        raise HTTPException(status_code=500, detail="Could not generate upload URL")
    return {"url": url, "key": file_key}

@router.post("/{session_id}/uploaded")
def mark_uploaded(session_id: str, key: str = Query(...), db: Session = Depends(deps.get_db)):
    session = session_service.handle_upload_finish(db, session_id, key)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/{session_id}/confirm", response_model=SessionResponse)
def confirm_session(session_id: str, db: Session = Depends(deps.get_db)):
    session = session_service.confirm_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
