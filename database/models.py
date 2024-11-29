from sqlalchemy import Column, String, DateTime, Boolean
from database.db import Base    
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class Blog(Base):
    __tablename__ = "blogs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String)
    body = Column(String)
    user_id = Column(UUID(as_uuid=True),default="user")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)  