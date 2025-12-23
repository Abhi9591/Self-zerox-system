
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.session import Session as SessionModel, SessionStatus
import uuid

def create_payment(db: Session, session_id: str, amount: float):
    payment = Payment(
        session_id=session_id,
        amount=amount,
        payment_status="PENDING"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def process_payment_success(db: Session, session_id: str, transaction_id: str):
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        return None
        
    payment = session.payment
    if not payment:
        payment = create_payment(db, session_id, session.total_amount)
    
    payment.payment_status = "SUCCESS"
    payment.transaction_id = transaction_id
    
    session.status = SessionStatus.PAID
    
    db.commit()
    db.refresh(session)
    return session
