"""
Pydantic схемы для семей и пользователей
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str = Field(..., max_length=100)
    username: str = Field(..., max_length=50, min_length=3)
    role: str = Field(..., pattern="^(parent|child)$")
    avatar_url: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class User(UserBase):
    id: uuid.UUID
    family_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FamilyBase(BaseModel):
    name: str = Field(..., max_length=100)


class FamilyCreate(FamilyBase):
    parent_name: str = Field(..., max_length=100)
    parent_username: str = Field(..., max_length=50, min_length=3)
    parent_password: str = Field(..., min_length=6, max_length=100)


class FamilyJoin(BaseModel):
    passcode: str = Field(..., min_length=6, max_length=6)
    user_name: str = Field(..., max_length=100)
    username: str = Field(..., max_length=50, min_length=3)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(..., pattern="^(parent|child)$")


class Family(FamilyBase):
    id: uuid.UUID
    passcode: str
    settings: Optional[dict] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FamilyWithMembers(Family):
    members: List[User] = []


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class FamilyCreateResponse(AuthResponse):
    family_id: uuid.UUID
    passcode: str
    parent: User


class FamilyMembersResponse(BaseModel):
    family: Family
    members: List[User]