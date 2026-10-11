from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",
        extra="ignore",
    )

    host:str = "localhost"
    port:int = 5432
    name:str
    user:str
    password:str

    @property
    def url(self) -> URL:
        return URL.create(
            drivername = "postgresql+psycopg",
            username = self.user,
            password = self.password,
            host = self.host,
            port = self.port,
            database = self.name,
        )

db_settings = DatabaseSettings()