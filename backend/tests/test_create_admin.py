from app.core.security import (
    verify_password,
)
from app.domain.user import UserRole
from app.repositories.user import (
    UserRepository,
)
from app.schemas.user import UserCreate
from app.scripts import create_admin
from tests.conftest import (
    TestingSessionLocal,
)


def test_create_admin_bootstrap(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        create_admin,
        "SessionLocal",
        TestingSessionLocal,
    )

    credentials = UserCreate(
        email="bootstrap-admin@example.com",
        password="StrongPassword123!",
    )

    admin = create_admin.create_or_update_admin(credentials)

    assert admin.email == ("bootstrap-admin@example.com")

    assert admin.role == (UserRole.admin)

    assert admin.is_active is True

    db = TestingSessionLocal()

    try:
        repository = UserRepository(db)

        stored_admin = repository.get_by_email("bootstrap-admin@example.com")

        assert stored_admin is not None

        assert stored_admin.role == (UserRole.admin)

        assert verify_password(
            "StrongPassword123!",
            stored_admin.hashed_password,
        )

    finally:
        db.close()
