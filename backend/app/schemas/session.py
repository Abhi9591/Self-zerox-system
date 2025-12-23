
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class SessionCreate(BaseModel):
    machine_id: int # Or machine_code encoded in token? Usually session starts at Kiosk, so machine_id is known.

class SessionResponse(BaseModel):
    session_id: str
    status: str
    page_count: int
    price_per_page: float
    total_amount: float
    file_name: Optional[str] = None
    preview_ready: bool
    confirmed: bool
    created_at: datetime
    
    upload_url: Optional[str] = None # Helper for frontend, actually constructed from QR
    
    class Config:
        orm_mode = True
