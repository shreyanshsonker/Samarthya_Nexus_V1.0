from pydantic import BaseModel, EmailStr
from uuid import UUID

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: str | None = None

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    household_id: UUID | None = None
    
    class Config:
        from_attributes = True

class HouseholdCreate(BaseModel):
    name: str
    location: str
    inverter_type: str
    capacity_kw: float
    grid_zone: str

class HouseholdResponse(HouseholdCreate):
    household_id: UUID
    
    class Config:
        from_attributes = True
