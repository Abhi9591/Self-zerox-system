
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String, unique=True, index=True, nullable=False) # e.g. KIOSK-001
    name = Column(String, nullable=True)
    price_per_page = Column(Float, default=5.0) # Default 5 rupees/cents
    is_active = Column(Boolean, default=True)

    # Relationship
    admin_map = relationship("AdminMachineMap", back_populates="machine", uselist=False)
    sessions = relationship("Session", back_populates="machine")


