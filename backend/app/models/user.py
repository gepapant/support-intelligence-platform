from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.user import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.agent,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )