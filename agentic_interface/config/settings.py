from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_HOST: str
    PINECONE_INDEX: str
    PINECONE_EMBEDDING_MODEL: str

    PUBLIC_IP: str
    DATABASE_NAME: str
    USERNAME: str
    PASSWORD: str
    DB_PORT: int
    INSTANCE_CONNECTION_NAME: str
    LOCAL_MODE: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
