from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    memberships = relationship("Membership", back_populates="user")
    clients = relationship("Client", back_populates="user")
    cases = relationship("Case", back_populates="user")
    events = relationship("Event", back_populates="user")

class Org(Base):
    __tablename__ = "orgs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    memberships = relationship("Membership", back_populates="org")
    clients = relationship("Client", back_populates="org")
    cases = relationship("Case", back_populates="org")
    events = relationship("Event", back_populates="org")

class Membership(Base):
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    role = Column(String, nullable=False)  # owner, admin, lawyer, assistant
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
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
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    user = relationship("User", back_populates="clients")
    org = relationship("Org", back_populates="clients")
    cases = relationship("Case", back_populates="client")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    case_no = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")  # active, pending, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    user = relationship("User", back_populates="cases")
    org = relationship("Org", back_populates="cases")
    client = relationship("Client", back_populates="cases")
    events = relationship("Event", back_populates="case")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"))
    title = Column(String, nullable=False)
    type = Column(String)
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True))
    location = Column(String)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="events")
    org = relationship("Org", back_populates="events")
    case = relationship("Case", back_populates="events")
