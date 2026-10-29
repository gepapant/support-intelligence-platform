from pydantic import (
    Field,
    SecretStr,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from sqlalchemy import URL, make_url


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",
        extra="ignore",
    )

    database_url: str | None = Field(
        default=None,
        validation_alias="DATABASE_URL",
    )

    host: str = "localhost"
    port: int = 5432
    name: str | None = None
    user: str | None = None
    password: str | None = None

    @model_validator(mode="after")
    def validate_database_configuration(
        self,
    ):
        if self.database_url:
            return self

        missing = [
            field_name
            for field_name in (
                "name",
                "user",
                "password",
            )
            if getattr(
                self,
                field_name,
            )
            is None
        ]

        if missing:
            missing_fields = ", ".join(missing)

            raise ValueError(f"Missing database configuration: {missing_fields}")

        return self

    @property
    def url(self) -> URL:
        if self.database_url:
            parsed_url = make_url(self.database_url)

            return parsed_url.set(drivername=("postgresql+psycopg"))

        assert self.name is not None
        assert self.user is not None
        assert self.password is not None

        return URL.create(
            drivername=("postgresql+psycopg"),
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AUTH_",
        extra="ignore",
    )

    secret_key: str = Field(min_length=32)

    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AI_",
        extra="ignore",
    )

    provider: str = "rule_based"

    api_key: SecretStr | None = None

    model: str = "gpt-6-luna"


class QueueSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="QUEUE_",
        extra="ignore",
    )

    broker_url: str = "redis://localhost:6379/0"

    result_backend: str = "redis://localhost:6379/1"


db_settings = DatabaseSettings()
auth_settings = AuthSettings()
ai_settings = AISettings()
queue_settings = QueueSettings()
