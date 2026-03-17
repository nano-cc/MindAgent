from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:123456@localhost:5432/chatmind"

    # LLM API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    ZHIPUAI_API_KEY: str = ""

    # Email Configuration
    EMAIL_HOST: str = "smtp.qq.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    # Application
    APP_NAME: str = "chatmind-python"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True

    # Document Storage
    DOCUMENT_STORAGE_PATH: str = "./data/documents"

    # Vector Database
    VECTOR_DB_PATH: str = "./data/chroma"

    # Agent Configuration
    MAX_AGENT_STEPS: int = 20
    MAX_CHAT_MESSAGES: int = 20

    # CORS
    CORS_ORIGINS: str = "*"


settings = Settings()
