import os
from getpass import getpass

from pydantic import ValidationError

from app.core.security import (
    hash_password,
)
from app.db.session import SessionLocal
from app.domain.user import UserRole
from app.models.user import User
from app.repositories.user import (
    UserRepository,
)
from app.schemas.user import UserCreate


def get_admin_credentials() -> UserCreate:
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL")

    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")

    if not email:
        email = input("Admin email: ").strip()

    if not password:
        password = getpass("Admin password: ")

    try:
        return UserCreate(
            email=email,
            password=password,
        )

    except ValidationError as exc:
        raise SystemExit(f"Invalid admin credentials:\n{exc}") from exc


def create_or_update_admin(
    credentials: UserCreate,
) -> User:
    db = SessionLocal()

    try:
        repository = UserRepository(db)

        email = str(credentials.email).lower()

        existing_user = repository.get_by_email(email)

        if existing_user is not None:
            existing_user.role = UserRole.admin

            existing_user.is_active = True

            existing_user.hashed_password = hash_password(credentials.password)

            db.commit()
            db.refresh(existing_user)

            return existing_user

        admin = User(
            email=email,
            hashed_password=(hash_password(credentials.password)),
            role=UserRole.admin,
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        return admin

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def main():
    credentials = get_admin_credentials()

    admin = create_or_update_admin(credentials)

    print(f"Admin account ready: {admin.email}")


if __name__ == "__main__":
    main()
