from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'sqlalchemy'
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithms'
    mail_username: str = 'mail_username'
    mail_password: str = 'mail_'
    mail_from: str = 'mail_from'
    mail_port: int = 465
    mail_server: str = 'mail_server'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = 'cloudinary'
    cloudinary_api_key: str = 'cloudinary_api_key'
    cloudinary_api_secret: str = 'cloudinary_api_secret'

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )


settings = Settings()
