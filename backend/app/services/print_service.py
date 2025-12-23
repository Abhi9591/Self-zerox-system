
import subprocess
import os
from sqlalchemy.orm import Session
from app.models.print_job import PrintJob
from app.models.session import Session as SessionModel, SessionStatus
from app.services.storage_service import storage_service
from app.core.config import settings

def send_to_printer(db: Session, session_id: str):
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session or session.status != SessionStatus.PAID:
        return None

    # Implement Print Logic
    # 1. Download file
    # 2. Send to CUPS
    # 3. Update status
    
    file_key = session.cloud_file_url
    local_path = f"print_{session_id}.pdf"
    
    try:
        storage_service.download_file(file_key, local_path)
        
        # CUPS Command: lp -d PrinterName -n Copies Filename
        # Assuming 1 copy for now as per minimal reqs, can extend later
        cmd = ["lp", "-d", settings.PRINTER_NAME, local_path]
        
        # Check if lp exists (for dev environment fallback)
        import shutil
        if shutil.which("lp"):
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print_status = "COMPLETED"
            else:
                print(f"Print failed: {result.stderr}")
                print_status = "FAILED"
        else:
            print("lp command not found, simulating print")
            print_status = "COMPLETED_SIMULATED"
            
        print_job = PrintJob(
            session_id=session_id,
            status=print_status
        )
        db.add(print_job)
        
        if "COMPLETED" in print_status:
            session.status = SessionStatus.PRINTED
            
        db.commit()
        
    except Exception as e:
        print(f"Printing error: {e}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
            
    return session
