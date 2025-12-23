
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services import payment_service, print_service
from app.models.session import Session as SessionModel
from app.utils.qr import generate_qr_base64

router = APIRouter()

@router.post("/{session_id}/create")
def create_payment(session_id: str, db: Session = Depends(deps.get_db)):
    # In real world, call Payment Gateway API
    # Here, just return a mock payment link/QR
    # The QR would point to a payment page or UPI deep link
    payment_link = f"upi://pay?pa=mock@upi&pn=XeroxKiosk&am=10.00&tr={session_id}"
    qr_base64 = generate_qr_base64(payment_link)
    return {"payment_url": payment_link, "qr_code": qr_base64}

@router.post("/{session_id}/mock-success")
def mock_payment_success(session_id: str, db: Session = Depends(deps.get_db)):
    # This simulates a webhook from payment provider
    session = payment_service.process_payment_success(db, session_id, "TXN_MOCK_123")
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Auto print
    print_service.send_to_printer(db, session_id)
    
    return {"status": "success", "print_status": "queued"}
