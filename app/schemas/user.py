from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str

    address_line: Optional[str] = None
    area: Optional[str] = None
    zipcode: Optional[str] = None
    city_id: int
    bank_id: int
    branch_id: int


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
    bank_name: str
    branch_name: str

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

class CityResponse(BaseModel):
    city_name: str
    state: str
    country: str

    class Config:
        from_attributes = True


class UserWithAccountResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    city: CityResponse
    account: AccountResponse

    class Config:
        from_attributes = True
