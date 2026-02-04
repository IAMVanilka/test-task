from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import MetaData

from modules.db.database import metadata_obj

from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"

class Base(DeclarativeBase):
    pass

class UsersOrm(Base):
    __tablename__ = 'users'
    metadata = metadata_obj
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.user)
    token: Mapped[str] = mapped_column(nullable=True)
