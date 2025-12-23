
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class PrintJob(Base):
    __tablename__ = "print_jobs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), unique=True, nullable=False)
    cups_job_id = Column(Integer, nullable=True)
    status = Column(String, default="QUEUED") # QUEUED, PROCESSING, COMPLETED, FAILED
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("Session", back_populates="print_job")
