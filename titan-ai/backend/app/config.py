from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "TITAN AI"
    database_url: str = "sqlite:///./titan.db"
    api_key: str = ""
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    cors_origins: str = "http://localhost:5173"
    class Config:
        env_file = ".env"

settings = Settings()
