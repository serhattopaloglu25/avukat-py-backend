"""Authentication routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import verify_password, get_password_hash, create_access_token
from app.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=schemas.Token)
async def register(
    user_data: schemas.UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = models.User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default organization
    new_org = models.Org(name=f"{user_data.name or user_data.email}'s Organization")
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    # Create membership (owner role)
    new_membership = models.Membership(
        user_id=new_user.id,
        org_id=new_org.id,
        role=models.RoleEnum.owner
    )
    db.add(new_membership)
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={
            "user_id": new_user.id,
            "org_id": new_org.id,
            "role": models.RoleEnum.owner.value
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    # Find user by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user's first organization and membership
    membership = db.query(models.Membership).filter(
        models.Membership.user_id == user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no organization membership"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "org_id": membership.org_id,
            "role": membership.role.value
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.MeResponse)
async def get_me(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    # Get user with memberships
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    # Get memberships with org data
    memberships = db.query(models.Membership).filter(
        models.Membership.user_id == user.id
    ).all()
    
    # Get current org
    current_org = db.query(models.Org).filter(
        models.Org.id == current_user.current_org_id
    ).first()
    
    return {
        "user": user,
        "memberships": memberships,
        "current_org": current_org
    }
