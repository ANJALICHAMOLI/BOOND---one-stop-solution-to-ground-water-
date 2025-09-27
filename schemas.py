from pydantic import BaseModel, EmailStr
from typing import Optional

# ---------- User Schemas ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------- Token Schemas ----------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


# ---------- Feature Schemas ----------
class FeasibilityRequest(BaseModel):
    location: str
    roof_area: float
    open_space: float


class CostRequest(BaseModel):
    harvesting_type: str
    location: str
