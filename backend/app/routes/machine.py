
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services import machine_service
from app.schemas.machine import MachineCreate, MachineUpdate, MachineResponse
from app.models.admin import Admin

router = APIRouter()

@router.post("/activate", response_model=MachineResponse)
def activate_machine(
    machine_in: MachineCreate,
    current_admin: Admin = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    try:
        machine = machine_service.create_machine_binding(
            db, 
            admin_id=current_admin.id, 
            machine_code=machine_in.machine_code
        )
        return machine
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{machine_id}/price", response_model=MachineResponse)
def set_price(
    machine_id: int,
    price_update: MachineUpdate,
    current_admin: Admin = Depends(deps.get_current_admin),
    db: Session = Depends(deps.get_db)
):
    # Verify ownership
    if not current_admin.machine_map or current_admin.machine_map.machine_id != machine_id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this machine")
        
    machine = machine_service.update_machine_price(db, machine_id, price_update.price_per_page)
    if not machine:
         raise HTTPException(status_code=404, detail="Machine not found")
    return machine
