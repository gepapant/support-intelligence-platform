from app.core.security import hash_password, verify_password
from app.domain.user import UserRole
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(
        self,
        user_data: UserCreate,
    ) -> User:
        email = user_data.email.lower()

        existing_user = self.repository.get_by_email(email)

        if existing_user is not None:
            raise UserAlreadyExistsError

        user = User(
            email=email,
            hashed_password=hash_password(user_data.password),
            role=UserRole.agent,
            is_active=True,
        )

        return self.repository.add(user)

    def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User | None:
        user = self.repository.get_by_email(email.lower())

        if user is None:
            return None

        if not user.is_active:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        return user

    def list_users(self) -> list[User]:
        return self.repository.get_all()
