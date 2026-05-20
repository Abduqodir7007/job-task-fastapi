from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from enum import Enum


class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    payment = "payment"
    reports = "reports"


class RoleSchema(BaseModel):
    """Role response schema."""

    id: int
    name: RoleEnum

    class Config:
        from_attributes = True


class UserRegisterSchema(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role_ids: List[int]

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password has special characters."""
        special_characters = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        if not any(ch in special_characters for ch in v):
            raise ValueError("Password must contain at least one special character.")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v):
        """Validate names contain only letters."""
        if not v.isalpha():
            raise ValueError("Name must contain letters only.")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        return v


class UserLoginSchema(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    """User response schema."""

    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    roles: List[RoleSchema]

    class Config:
        from_attributes = True


class UserDetailSchema(BaseModel):
    """User detail schema."""

    id: int
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    """Admin user create schema."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role_ids: List[int]

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        special_characters = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        if not any(ch in special_characters for ch in v):
            raise ValueError("Password must contain at least one special character.")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v):
        if not v.isalpha():
            raise ValueError("Name must contain letters only.")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        return v


class UserUpdateSchema(BaseModel):
    """Admin user update schema."""

    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        special_characters = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        if not any(ch in special_characters for ch in v):
            raise ValueError("Password must contain at least one special character.")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v):
        if v is None:
            return v
        if not v.isalpha():
            raise ValueError("Name must contain letters only.")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        return v
