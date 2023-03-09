import datetime
from types import NoneType
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class Message(BaseModel):
    x_request_id: str | NoneType
    notice_id: UUID
    users_id: List[UUID]
    template_id: int | NoneType = 1
    extra: dict = Field(default_factory=dict)
    transport: str
    priority: str | NoneType = 0
    msg_type: int | NoneType
    text: str
    expire_at: datetime.datetime

