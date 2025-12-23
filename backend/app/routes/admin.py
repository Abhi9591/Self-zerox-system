
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.services import auth_service
from app.schemas.admin import AdminCreate, AdminResponse
from app.schemas.token import Token
from app.core import jwt
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=AdminResponse)
def register(admin_in: AdminCreate, db: Session = Depends(deps.get_db)):
    admin = auth_service.get_admin_by_username(db, admin_in.username)
    if admin:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    admin = auth_service.create_admin(db, admin_in)
    return admin

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)):
    admin = auth_service.authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = jwt.create_access_token(subject=admin.id)
    return {"access_token": access_token, "token_type": "bearer"}
