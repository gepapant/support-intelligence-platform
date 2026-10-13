from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.user import (
    UserAlreadyExistsError,
    UserService,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    repository = UserRepository(db)

    return UserService(repository)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    try:
        return service.register_user(user_data)

    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    credentials: LoginRequest,
    service: UserService = Depends(get_user_service),
):
    user = service.authenticate_user(
        email=credentials.email,
        password=credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    access_token = create_access_token(user_id=user.id)

    return TokenResponse(
        access_token=access_token,
    )


@router.get(
    "/me",
    response_model=UserRead,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
