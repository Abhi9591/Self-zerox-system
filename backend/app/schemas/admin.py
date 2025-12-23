
from pydantic import BaseModel

class AdminBase(BaseModel):
    username: str

class AdminCreate(AdminBase):
    password: str
    machine_code: str # Required for initial 1:1 binding

class AdminResponse(AdminBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
