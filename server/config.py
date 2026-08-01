from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str
    DB_HOST: str
    DB_PORT: int

    @property
    def DATABASE_URL(self) -> str:
        return (
            f'mysql+asyncmy://'
            f'{self.MYSQL_USER}:'
            f'{self.MYSQL_PASSWORD}@'
            f'{self.DB_HOST}:'
            f'{self.DB_PORT}'
            f'{self.MYSQL_DATABASE}'
        )

    BASE_URL: str
    UPLOAD_DIR: Path = Path('static/app')

    model_config = SettingsConfigDict(env_file=('.env.database', '.env.server'))


settings = Settings()
