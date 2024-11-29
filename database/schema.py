
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from enum import Enum
from uuid import UUID
from datetime import datetime


class Role(str,Enum):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
      


class User(BaseModel):
    email: EmailStr

class UserCreate(User):
    password: str
    role: Role
    class Config:
        from_attributes = True

class UserLogin(User):
    password: str

class UserResponse(User):
    id: UUID
    is_active: bool
    role: Role


class UpdateUser(BaseModel):
    id: Optional[UUID]
    role: Optional[Role]
    email: Optional[EmailStr]
    password: str
    
    class Config:
        from_attributes = True

class Blog(BaseModel):
    title: str
    body: str
    user_id: str
class BlogCreate(Blog):
    class Config:
        from_attributes = True

class BlogResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    

class Token(BaseModel):
    access_token: str
    token_type: str