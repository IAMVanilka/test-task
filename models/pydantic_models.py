from pydantic import BaseModel, EmailStr, Field
from models.db_models import UserRole

class UserModel(BaseModel):
    username: str = Field(..., description="Уникальное имя пользователя")

class UserWithPassword(UserModel):
    password: str = Field(..., description="Пароль пользователя", example="Strong_Password_123%")

class UserForRegistration(UserWithPassword):
    email: EmailStr | None = Field(None, description="Email (опционально)", example="user@example.com")
    role: UserRole = Field(
        default=UserRole.user,
        description="Роль пользователя",
        examples=["user", "admin", "superadmin"],
    )

class UserForUpdate(UserModel):
    new_username: str | None = Field(None, description="Новое имя пользователя, которое вы хотите задать.")
    password: str | None = Field(None, description="Пароль пользователя", example="Strong_Password_123%")
    email: EmailStr | None = Field(None, description="Email (опционально)", example="user@example.com")
    role: UserRole | None = Field(
        default=None,
        description="Роль пользователя",
        examples=["user", "admin", "superadmin"],
    )