
from sqlalchemy.orm import Session
from app.models.admin import Admin
from app.schemas.admin import AdminCreate
from app.core.security import get_password_hash, verify_password

def get_admin_by_username(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()

def create_admin(db: Session, admin_in: AdminCreate) -> Admin:
    hashed_password = get_password_hash(admin_in.password)
    db_admin = Admin(
        username=admin_in.username,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def authenticate_admin(db: Session, username: str, password: str):
    admin = get_admin_by_username(db, username)
    if not admin:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin
