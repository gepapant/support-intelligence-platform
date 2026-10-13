from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_admin
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserRead
from app.services.user import UserService


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[
        Depends(require_admin),
    ],
)


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    repository = UserRepository(db)

    return UserService(repository)


@router.get(
    "/users",
    response_model=list[UserRead],
)
def list_users(
    service: UserService = Depends(get_user_service),
):
    return service.list_users()