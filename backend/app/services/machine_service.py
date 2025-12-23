
from sqlalchemy.orm import Session
from app.models.machine import Machine
from app.models.map import AdminMachineMap
from app.models.admin import Admin
from app.schemas.machine import MachineCreate, MachineUpdate

def get_machine_by_code(db: Session, machine_code: str):
    return db.query(Machine).filter(Machine.machine_code == machine_code).first()

def create_machine_binding(db: Session, admin_id: int, machine_code: str):
    # Check if machine exists
    machine = get_machine_by_code(db, machine_code)
    if not machine:
        # Create new machine if not exists (Activation flow)
        machine = Machine(machine_code=machine_code, name=f"Kiosk {machine_code}")
        db.add(machine)
        db.commit()
        db.refresh(machine)
    
    # Check if already bound
    existing_map = db.query(AdminMachineMap).filter(AdminMachineMap.machine_id == machine.id).first()
    if existing_map:
        if existing_map.admin_id != admin_id:
            raise ValueError("Machine already bound to another admin")
        return machine # Already bound to this admin

    # Create binding
    new_map = AdminMachineMap(admin_id=admin_id, machine_id=machine.id)
    db.add(new_map)
    db.commit()
    return machine

def update_machine_price(db: Session, machine_id: int, price: float):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if machine:
        machine.price_per_page = price
        db.commit()
        db.refresh(machine)
    return machine
