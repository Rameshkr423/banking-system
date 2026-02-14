from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str

    address_line: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    zipcode: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str

    class Config:
        from_attributes = True
        
class AccountResponse(BaseModel):
    account_number: str
    account_type: str

    class Config:
        from_attributes = True


class UserWithAccountResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    account: AccountResponse

    class Config:
        from_attributes = True
