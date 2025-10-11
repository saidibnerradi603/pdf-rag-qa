from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIKeysSettings(BaseSettings):
    """API keys configuration settings."""
    google_api_key: SecretStr = Field(..., description="Google API Key", env="GOOGLE_API_KEY")
    cohere_api_key: SecretStr = Field(..., description="Cohere API Key", env="COHERE_API_KEY")
    pinecone_api_key: SecretStr = Field(..., description="Pinecone API Key", env="PINECONE_API_KEY")
    llama_cloud_api_key: SecretStr = Field(..., description="LlamaCloud API Key", env="LLAMA_CLOUD_API_KEY")

    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    """Main application settings."""
    project_name: str = "PDF RAG QA System"
    version: str = "0.1.0"

    api_keys: APIKeysSettings = Field(default_factory=APIKeysSettings)


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )


def get_settings():
    return Settings()
