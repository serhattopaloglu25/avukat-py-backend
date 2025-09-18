"""Pydantic schemas for request/response models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Email validation
try:
    from pydantic import EmailStr
except ImportError:
    EmailStr = str


class RoleEnum(str, Enum):
    owner = "owner"
    admin = "admin"
    lawyer = "lawyer"
    assistant = "assistant"

class CaseStatusEnum(str, Enum):
    active = "active"
    pending = "pending"
    closed = "closed"

# User Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: Optional[str] = None

class UserLogin(BaseModel):
    username: EmailStr  # OAuth2 expects 'username' field
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int
    org_id: int
    role: str

# Org Schemas
class OrgResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Membership Schemas
class MembershipResponse(BaseModel):
    id: int
    role: RoleEnum
    org: OrgResponse
    
    class Config:
        from_attributes = True

# Client Schemas
class ClientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Case Schemas
class CaseCreate(BaseModel):
    client_id: int
    case_number: str
    title: str
    status: Optional[CaseStatusEnum] = CaseStatusEnum.active

class CaseUpdate(BaseModel):
    client_id: Optional[int] = None
    case_number: Optional[str] = None
    title: Optional[str] = None
    status: Optional[CaseStatusEnum] = None

class CaseResponse(BaseModel):
    id: int
    client_id: int
    case_number: str
    title: str
    status: CaseStatusEnum
    created_at: datetime
    updated_at: datetime
    client: Optional[ClientResponse] = None
    
    class Config:
        from_attributes = True

# Event Schemas
class EventCreate(BaseModel):
    case_id: Optional[int] = None
    title: str
    type: Optional[str] = None
    starts_at: datetime
    ends_at: Optional[datetime] = None
    location: Optional[str] = None

class EventUpdate(BaseModel):
    case_id: Optional[int] = None
    title: Optional[str] = None
    type: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    location: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    case_id: Optional[int]
    title: str
    type: Optional[str]
    starts_at: datetime
    ends_at: Optional[datetime]
    location: Optional[str]
    created_at: datetime
    case: Optional[CaseResponse] = None
    
    class Config:
        from_attributes = True

# Stats Schema
class StatsResponse(BaseModel):
    total_clients: int
    total_cases: int
    active_cases: int
    upcoming_events: int

# Me Response
class MeResponse(BaseModel):
    user: UserResponse
    memberships: List[MembershipResponse]
    current_org: OrgResponse
