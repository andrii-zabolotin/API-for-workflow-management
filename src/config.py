from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from os import environ

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    # db_url: str = Field(..., json_schema_extra={"env": "DB_URL"})
    db_url: str = f"postgresql+asyncpg://postgres:{environ.get('PASSWORD')}@localhost:5432/Workflow?async_fallback=True"
    db_echo: bool = True


settings = Settings()
