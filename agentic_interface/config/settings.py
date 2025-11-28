"""
Application Settings Configuration

Loads and validates environment variables using Pydantic.
Provides type-safe access to configuration values.

Environment variables are loaded from .env file in the project root.

Configuration categories:
- OpenAI: API key for GPT-4 chat model
- Pinecone: Vector database for RAG (embeddings, host, namespaces)
- Database: PostgreSQL connection details for user data
- Runtime: Local vs production mode flags
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration with automatic .env file loading
    
    All values are required unless specified with Optional.
    Pydantic will raise ValidationError if required vars are missing.
    """
    # OpenAI Configuration
    OPENAI_API_KEY: str  # API key for GPT-4 model
    
    # Pinecone Vector Database Configuration
    PINECONE_API_KEY: str  # API key for Pinecone
    PINECONE_HOST: str  # Pinecone index host URL
    PINECONE_NAMESPACE_1: str  # Primary namespace (e.g., Huberman content)
    PINECONE_NAMESPACE_2: str  # Secondary namespace (e.g., Goggins content)
    PINECONE_EMBEDDING_MODEL: str  # HuggingFace model for embeddings

    # Database Configuration
    PUBLIC_IP: str  # PostgreSQL host IP (for local mode)
    DATABASE_NAME: str  # Name of the database
    USERNAME: str  # Database username
    PASSWORD: str  # Database password
    DB_PORT: int  # Database port (default: 5432)
    INSTANCE_CONNECTION_NAME: str  # GCP Cloud SQL instance name
    LOCAL_MODE: str  # "true" for local, "false" for GCP

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"

# Singleton instance - import this in other modules
settings = Settings()
