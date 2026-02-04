from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from models.db_models import UserRole

class BaseResponse(BaseModel):
    msg: str = Field(..., description="Сообщение о результате операции")

class UserDataResponse(BaseModel):
    id: int = Field(..., description="Уникальный ID пользователя")
    username: str = Field(..., description="Имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Email (если указан)")
    role: UserRole = Field(..., description="Роль пользователя", examples=["user", "admin", "superadmin"])

    class Config:
        from_attributes = True

class AuthorizationResponse(BaseModel):
    x_api_token: str = Field(..., description="API токен пользователя")

class UserUpdateResponse(BaseResponse):
    username: str = Field(..., description="Старое имя пользователя")
    new_username: str = Field(..., description="Новое имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Новый Email (если указан)")
    role: UserRole = Field(..., description="Новая роль пользователя", examples=["user", "admin", "superadmin"])