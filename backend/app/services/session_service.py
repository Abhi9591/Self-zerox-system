
import string
import random
import uuid
import os
import pypdf
from sqlalchemy.orm import Session
from app.models.session import Session as SessionModel, SessionStatus
from app.schemas.session import SessionCreate
from app.services.storage_service import storage_service
from app.utils.qr import generate_qr_base64
from app.core.config import settings

def generate_session_id():
    return str(uuid.uuid4())

def create_session(db: Session, machine_id: int):
    session_id = generate_session_id()
    db_session = SessionModel(
        session_id=session_id,
        machine_id=machine_id,
        status=SessionStatus.CREATED
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: str):
    return db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

def handle_upload_finish(db: Session, session_id: str, file_key: str):
    print(f"DEBUG: handle_upload_finish id={session_id} key={file_key}")
    session = get_session(db, session_id)
    if not session:
        print("DEBUG: Session not found")
        return None
    
    temp_path = f"temp_{session_id}.pdf"
    print(f"DEBUG: Downloading to {temp_path}")
    storage_service.download_file(file_key, temp_path)
    
    try:
        with open(temp_path, "rb") as f:
            pdf = pypdf.PdfReader(f)
            page_count = len(pdf.pages)
        print(f"DEBUG: PDF Valid. Pages={page_count}")
    except Exception as e:
        print(f"DEBUG: PDF Read Error: {e}")
        page_count = 0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    session.cloud_file_url = file_key
    session.file_name = file_key 
    session.page_count = page_count if page_count > 0 else 1 # Fallback to 1
    
    if session.machine:
        session.price_per_page = session.machine.price_per_page
    
    session.total_amount = session.page_count * session.price_per_page
    session.status = SessionStatus.UPLOADED
    session.preview_ready = True
    
    db.commit()
    db.refresh(session)
    print("DEBUG: Session Updated Successfully")
    return session

def confirm_session(db: Session, session_id: str):
    session = get_session(db, session_id)
    if session:
        session.confirmed = True
        session.status = SessionStatus.CONFIRMED
        db.commit()
        db.refresh(session)
    return session
