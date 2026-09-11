from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Document Intelligence API"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: str = "sqlite:///./document_intelligence.db"

    ocr_enabled: bool = True
    llm_api_key: str = ""
    llm_model: str = ""
    financial_tolerance: float = 0.01

    class Config:
        env_file = ".env"


settings = Settings()