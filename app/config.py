from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://admin:admin@postgres:5432/documents_db"
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()