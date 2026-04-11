from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    supabase_jwt_secret: str

    # Database (direct Postgres connection for SQLAlchemy/Alembic)
    database_url: str

    # Redis / ARQ
    redis_url: str

    # OSV.dev
    osv_api_url: str = "https://api.osv.dev"

    # Envelope encryption — AES-256 key for API key encryption (magnus C1)
    # Must be a 32-byte hex string (64 hex chars). Generate with: openssl rand -hex 32
    encryption_key: str

    # App
    environment: str = "development"
    debug: bool = False
    allowed_origins: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
