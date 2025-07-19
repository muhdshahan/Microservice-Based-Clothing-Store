from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    username: str
    email: EmailStr
    
class UserCreate(UserBase):
    password: str
    role: str = "user"  # default role
    
class UserOut(UserBase):
    id: int 
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True