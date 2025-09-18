from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import User, Org, Membership
from app.schemas import UserLogin, UserRegister, Token, UserResponse
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_HOURS
)
from app.deps import get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get first membership for org_id
    membership = db.query(Membership).filter(Membership.user_id == user.id).first()
    
    token_data = {
        "user_id": user.id,
        "org_id": membership.org_id if membership else None,
        "role": membership.role if membership else None
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": membership.role if membership else None
        }
    }

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name or user_data.email.split('@')[0]
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default org
    org = Org(name=f"{user.name}'s Organization")
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Create membership as owner
    membership = Membership(
        user_id=user.id,
        org_id=org.id,
        role="owner"
    )
    db.add(membership)
    db.commit()
    
    # Auto login
    token_data = {
        "user_id": user.id,
        "org_id": org.id,
        "role": "owner"
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": "owner"
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user
