
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class SessionStatus(str, enum.Enum):
    CREATED = "CREATED"
    UPLOADED = "UPLOADED"
    PREVIEW_READY = "PREVIEW_READY"
    CONFIRMED = "CONFIRMED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID = "PAID"
    PRINTED = "PRINTED"

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, index=True) # UUID
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    
    status = Column(String, default=SessionStatus.CREATED, nullable=False)
    page_count = Column(Integer, default=0)
    price_per_page = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    cloud_file_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    
    preview_ready = Column(Boolean, default=False)
    confirmed = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    machine = relationship("Machine", back_populates="sessions")
    payment = relationship("Payment", back_populates="session", uselist=False)
    print_job = relationship("PrintJob", back_populates="session", uselist=False)


