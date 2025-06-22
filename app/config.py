from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    serper_api_key: str
    openai_api_key: str  # or deepseek_api_key
    model: str = "gpt-3.5-turbo"  # or "deepseek-chat"

    class Config:
        env_file = ".env"

settings = Settings()