from app.core.config import (
    DatabaseSettings,
)


def test_database_settings_accepts_database_url(
    monkeypatch,
):
    for variable in (
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ):
        monkeypatch.delenv(
            variable,
            raising=False,
        )

    monkeypatch.setenv(
        "DATABASE_URL",
        ("postgresql://render_user:secret@database.internal:5432/support_intelligence"),
    )

    settings = DatabaseSettings(_env_file=None)

    url = settings.url

    assert url.drivername == "postgresql+psycopg"

    assert url.username == ("render_user")

    assert url.password == "secret"

    assert url.host == ("database.internal")

    assert url.port == 5432

    assert url.database == ("support_intelligence")


def test_database_settings_accepts_local_fields(
    monkeypatch,
):
    monkeypatch.delenv(
        "DATABASE_URL",
        raising=False,
    )

    settings = DatabaseSettings(
        host="localhost",
        port=5432,
        name="support_intelligence",
        user="support_app",
        password="local-password",
        _env_file=None,
    )

    url = settings.url

    assert url.drivername == "postgresql+psycopg"

    assert url.host == "localhost"

    assert url.database == ("support_intelligence")

    assert url.username == ("support_app")
