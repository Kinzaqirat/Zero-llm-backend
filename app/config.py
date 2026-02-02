# """Application configuration."""

# from typing import List

# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     """Application settings."""

#     model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

#     # Application
#     APP_NAME: str = "CourseCompanionFTE"
#     APP_VERSION: str = "1.0.0"
#     DEBUG: bool = False
#     ENVIRONMENT: str = "development"

#     # Database
#     # If DATABASE_URL is set (e.g., a full postgres/Neon URL), that will be used.
#     # Otherwise the app uses a simple local SQLite file at `DATABASE_PATH`.
#     DATABASE_URL: str = ""
#     DATABASE_PATH: str = "data/dev.db"
#     DATABASE_POOL_SIZE: int = 10
#     DATABASE_MAX_OVERFLOW: int = 20

#     # Redis
#     REDIS_URL: str = "redis://localhost:6379/0"
#     REDIS_CACHE_TTL: int = 3600
#     # Timeout (seconds) for Redis network operations before falling back to SQLite
#     REDIS_OP_TIMEOUT: float = 0.5

#     # Cloudflare R2 / S3-compatible storage
#     CLOUDFLARE_R2_ACCESS_KEY_ID: str = ""
#     CLOUDFLARE_R2_SECRET_ACCESS_KEY: str = ""
#     CLOUDFLARE_R2_BUCKET_NAME: str = "course-companion-content"
#     CLOUDFLARE_R2_ENDPOINT_URL: str = ""
#     CLOUDFLARE_R2_REGION: str = "auto"

#     # CORS
#     CORS_ORIGINS: List[str] = ["https://chat.openai.com"]

#     # API
#     API_V1_PREFIX: str = "/api/v1"

#     # Security
#     JWT_SECRET_KEY: str = "change-this-in-production"
#     JWT_ALGORITHM: str = "HS256"
#     JWT_EXPIRATION_MINUTES: int = 1440

#     # Logging
#     LOG_LEVEL: str = "INFO"
#     LOG_FORMAT: str = "json"


# settings = Settings()

"""Application configuration."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Application
    APP_NAME: str = "CourseCompanionFTE"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # 👇 NEW: Base URL for ChatGPT Apps integration
    BASE_URL: str = "http://localhost:8000"
    # ⚠️ IMPORTANT: Change this to your deployed URL when deploying!
    # Example: "https://course-companion-api.up.railway.app"

    # Database
    # If DATABASE_URL is set (e.g., a full postgres/Neon URL), that will be used.
    # Otherwise the app uses a simple local SQLite file at `DATABASE_PATH`.
    DATABASE_URL: str = ""
    DATABASE_PATH: str = "data/dev.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    # Timeout (seconds) for Redis network operations before falling back to SQLite
    REDIS_OP_TIMEOUT: float = 0.5

    # Cloudflare R2 / S3-compatible storage
    CLOUDFLARE_R2_ACCESS_KEY_ID: str = ""
    CLOUDFLARE_R2_SECRET_ACCESS_KEY: str = ""
    CLOUDFLARE_R2_BUCKET_NAME: str = "course-companion-content"
    CLOUDFLARE_R2_ENDPOINT_URL: str = ""
    CLOUDFLARE_R2_REGION: str = "auto"

    # 👇 UPDATED: CORS - Added ChatGPT URLs
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",           # Local development
        "https://chat.openai.com",         # ChatGPT Apps (existing)
        "https://chatgpt.com",             # ChatGPT Apps (new URL)
        "https://cdn.jsdelivr.net",        # ChatGPT plugins CDN
    ]

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # 👇 NEW: ChatGPT Apps Configuration (Optional)
    CHATGPT_APP_NAME: str = "Course Companion"
    CHATGPT_APP_DESCRIPTION: str = "AI-powered Generative AI tutor with interactive lessons and quizzes"
    CHATGPT_CONTACT_EMAIL: str = "support@coursecompanion.com"  # Optional


settings = Settings()