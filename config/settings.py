from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_uri: str
    token_secret: str
    upload_dir: str
    max_images_per_activity: int
    max_image_size_mb: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings: Settings = Settings()
