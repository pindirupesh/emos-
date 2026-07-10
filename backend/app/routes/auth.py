from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models.db_models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---- Request Models (what the frontend sends) ----
class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ---- Signup Endpoint ----
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user (plaintext password is fine for hackathon)
    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=user.password  # In production, you'd hash this!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name,
        "message": "Signup successful!"
    }

# ---- Login Endpoint ----
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check password (plaintext comparison)
    if db_user.password_hash != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "name": db_user.name,
        "message": "Login successful!"
    }