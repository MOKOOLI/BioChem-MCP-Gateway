from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "BioChem MCP Gateway"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # External APIs
    RHEA_BASE_URL: str = "https://www.rhea-db.org/rhea"
    CHEBI_BASE_URL: str = "https://www.ebi.ac.uk/ols4/api"
    UNIPROT_BASE_URL: str = "https://rest.uniprot.org"
    ALPHAFOLD_BASE_URL: str = "https://alphafold.ebi.ac.uk/files"

    # Cache
    CACHE_TTL_SEMANTIC: int = 3600
    CACHE_TTL_RESULT: int = 86400
    CACHE_TTL_STRUCTURE: int = 604800

    # Paths
    DATA_DIR: str = "./data"
    STRUCTURE_DIR: str = "./data/structures"
    DOCKING_DIR: str = "./data/docking"

    # Observability
    OTEL_SERVICE_NAME: str = "biochem-mcp-gateway"
    JAEGER_ENDPOINT: str = "http://localhost:14268/api/traces"
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""


settings = Settings()