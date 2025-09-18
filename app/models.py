"""SQLAlchemy models for the application"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class RoleEnum(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    lawyer = "lawyer"
    assistant = "assistant"

class CaseStatusEnum(str, enum.Enum):
    active = "active"
    pending = "pending"
    closed = "closed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="user")
    cases = relationship("Case", back_populates="user")
    events = relationship("Event", back_populates="user")

class Org(Base):
    __tablename__ = "orgs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = relationship("Membership", back_populates="org", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="org")
    cases = relationship("Case", back_populates="org")
    events = relationship("Event", back_populates="org")

class Membership(Base):
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.lawyer, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="memberships")
    org = relationship("Org", back_populates="memberships")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'org_id', name='_user_org_uc'),
    )

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="clients")
    org = relationship("Org", back_populates="clients")
    cases = relationship("Case", back_populates="client")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    case_number = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    status = Column(Enum(CaseStatusEnum), default=CaseStatusEnum.active, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cases")
    org = relationship("Org", back_populates="cases")
    client = relationship("Client", back_populates="cases")
    events = relationship("Event", back_populates="case")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=True)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="events")
    org = relationship("Org", back_populates="events")
    case = relationship("Case", back_populates="events")
