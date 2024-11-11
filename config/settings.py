from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_uri: str
    token_secret: str
    upload_dir: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings: Settings = Settings()
