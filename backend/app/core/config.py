from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 5432
    name: str
    user: str
    password: str

    @property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
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


db_settings = DatabaseSettings()
auth_settings = AuthSettings()