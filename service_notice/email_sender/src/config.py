from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    SEND_FROM_EMAIL: str = Field("test@example.com", env="EMAIL_SENDER_FROM_EMAIL")
    DEBUG: bool = Field(True, env="EMAIL_SENDER_DEBUG")
    RABBITMQ_HOST: str = Field("localhost", env="RABBITMQ_NOTICE_HOST")
    RABBITMQ_PORT: int = Field(5672, env="RABBITMQ_NOTICE_PORT")
    EMAIL_QUEUE: str = "email"
    SENDGRID_API_KEY: str = "default_for_local_debug"


settings = Settings()
