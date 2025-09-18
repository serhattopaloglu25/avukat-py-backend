from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Auth Schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    consents: Optional[dict] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# User Schemas  
class UserBase(BaseModel):
    email: str
    name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Client Schemas
class ClientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientResponse(ClientCreate):
    id: int
    user_id: int
    org_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Case Schemas
class CaseCreate(BaseModel):
    client_id: int
    case_no: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class CaseUpdate(BaseModel):
    client_id: Optional[int] = None
    case_no: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class CaseResponse(CaseCreate):
    id: int
    user_id: int
    org_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Event Schemas
class EventCreate(BaseModel):
    case_id: Optional[int] = None
    title: str
    type: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None

class EventUpdate(BaseModel):
    case_id: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None

class EventResponse(EventCreate):
    id: int
    user_id: int
    org_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Stats Schema
class StatsResponse(BaseModel):
    total_clients: int
    total_cases: int
    active_cases: int
    upcoming_events: int
