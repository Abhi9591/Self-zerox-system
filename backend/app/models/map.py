
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class AdminMachineMap(Base):
    __tablename__ = "admin_machine_map"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), unique=True, nullable=False)
    machine_id = Column(Integer, ForeignKey("machines.id"), unique=True, nullable=False)

    admin = relationship("Admin", back_populates="machine_map")
    machine = relationship("Machine", back_populates="admin_map")
