from pydantic import Field, SecretStr,HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIKeysSettings(BaseSettings):
    """API keys configuration settings."""
    google_api_key: SecretStr = Field(..., description="Google API Key", env="GOOGLE_API_KEY")
    cohere_api_key: SecretStr = Field(..., description="Cohere API Key", env="COHERE_API_KEY")
    pinecone_api_key: SecretStr = Field(..., description="Pinecone API Key", env="PINECONE_API_KEY")
    llama_cloud_api_key: SecretStr = Field(..., description="LlamaCloud API Key", env="LLAMA_CLOUD_API_KEY")
    supabase_url: HttpUrl =  Field(..., description="Supabase Project URL", env="SUPABASE_URL")
    supabase_key: SecretStr =  Field(..., description="Supabase API Key", env="SUPABASE_KEY")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    """Main application settings."""
    project_name: str = "PDF RAG QA System"
    version: str = "0.1.0"

    api_keys: APIKeysSettings = Field(default_factory=APIKeysSettings)
    
    # File upload settings
    max_file_size_mb: int = 5
    allowed_mime_types: list[str] = ["application/pdf"]
    storage_bucket_name: str = "pdfs_files"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )


def get_settings():
    return Settings()
