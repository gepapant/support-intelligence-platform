import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

from app.core.security import create_access_token
from app.domain.user import UserRole
from app.models.user import User


TEST_DATABASE_URL = "sqlite://"


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def authenticated_client(client):
    db = TestingSessionLocal()

    user = User(
        email="test-agent@example.com",
        hashed_password="not-used-in-this-test",
        role=UserRole.agent,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        user_id=user.id
    )

    db.close()

    client.headers.update(
        {
            "Authorization": f"Bearer {token}"
        }
    )

    return client

@pytest.fixture()
def admin_client(client):
    db = TestingSessionLocal()

    user = User(
        email="admin@example.com",
        hashed_password="not-used-in-this-test",
        role=UserRole.admin,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        user_id=user.id
    )

    db.close()

    client.headers.update(
        {
            "Authorization": f"Bearer {token}"
        }
    )

    return client