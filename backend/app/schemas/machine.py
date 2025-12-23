
from typing import Optional
from pydantic import BaseModel

class MachineBase(BaseModel):
    name: Optional[str] = None
    price_per_page: Optional[float] = None

class MachineCreate(MachineBase):
    machine_code: str # KIOSK-XXXX

class MachineUpdate(BaseModel):
    price_per_page: float

class MachineResponse(MachineBase):
    id: int
    machine_code: str
    is_active: bool

    class Config:
        orm_mode = True
