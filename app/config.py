from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    serper_api_key: str
    openai_api_key: str
    model: str = "gpt-3.5-turbo"

    class Config:
        env_file = ".env"

settings = Settings()
