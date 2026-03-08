import logging
import warnings

from pydantic_settings import BaseSettings
from typing import Optional, List

_DEFAULT_SECRET = "changethis_secret_key_for_jwt"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Surplus Hub API"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "surplushub"
    DATABASE_URL: Optional[str] = None

    SECRET_KEY: str = _DEFAULT_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Redis
    REDIS_URL: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Clerk
    CLERK_PEM_PUBLIC_KEY: Optional[str] = None
    CLERK_JWKS_URL: Optional[str] = None

    # Server
    BASE_URL: str = "http://localhost:8000"

    # S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET_NAME: str = "surplus-hub-uploads"
    AWS_S3_REGION: str = "ap-northeast-2"

    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None

    # AI Services
    APP_ENV: str = "local"  # local | dev | stage | prod
    AI_PROVIDER: str = "default"  # default | vertex
    GOOGLE_AI_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: str = "asia-northeast3"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSION: int = 1024

    @property
    def use_vertex(self) -> bool:
        return self.AI_PROVIDER == "vertex"

    # Max upload
    MAX_UPLOAD_SIZE_MB: int = 10

    @property
    def use_local_embedding(self) -> bool:
        if self.use_vertex:
            return False
        return self.APP_ENV == "local"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **data):
        super().__init__(**data)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        if self.APP_ENV in ("production", "prod") and self.SECRET_KEY.startswith("changethis"):
            raise ValueError("SECRET_KEY must be changed in production!")
        if self.SECRET_KEY == _DEFAULT_SECRET:
            warnings.warn(
                "SECRET_KEY is using the default value. "
                "Set a strong random SECRET_KEY in .env for production.",
                stacklevel=2,
            )
        if self.APP_ENV != "local" and not self.use_vertex and not self.OPENAI_API_KEY:
            warnings.warn(
                f"APP_ENV={self.APP_ENV} requires OPENAI_API_KEY for embedding. "
                "Set OPENAI_API_KEY in .env or embedding will fail.",
                stacklevel=2,
            )
        if self.use_vertex and not self.GOOGLE_CLOUD_PROJECT:
            warnings.warn(
                "AI_PROVIDER=vertex requires GOOGLE_CLOUD_PROJECT. "
                "Set it in .env or Vertex AI calls will fail.",
                stacklevel=2,
            )

settings = Settings()
