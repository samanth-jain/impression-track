from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "impression_tracker"
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
