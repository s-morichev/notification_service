from types import NoneType
from typing import List

from pydantic import BaseModel


class Message(BaseModel):
    users_id: List[int]
    template_id: int | NoneType = 1
    text: str
    msg_type: int | NoneType
    priority: str | NoneType = 'low'
