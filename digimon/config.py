from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SQLDB_URL: str
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    
    model_config = SettingsConfigDict(env_file=".env")

def get_settings():
    return Settings()