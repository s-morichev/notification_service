from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("Producer", env="UGC_PROJECT_NAME")
    PRODUCER_DSN: str = Field("amqp://admin:admin@localhost:5672/", env="RABBITMQ_DSN")
    QUEUE_NAME: str = Field("notice", env="QUEUE_NAME")


settings = Settings(_env_file="../.env")
