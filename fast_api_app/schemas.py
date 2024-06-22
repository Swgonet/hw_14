from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    birthday_date: date
    phone_numbers: str = Field(min_length=10, max_length=13)
    email: EmailStr
    other_description: Optional[str]


class UserResponse(UserSchema):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    class Config:
        orm_mode = True


class UserResponses(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class EmailSchema(BaseModel):
    email: EmailStr


class RequestEmail(BaseModel):
    email: EmailStr
