from uuid import UUID
import requests
from http import HTTPStatus
import orjson
from core.models import UserInfo
from core.config import settings


def get_user_info(user_id: UUID) -> list[UserInfo]:
    auth_srv = settings.AUTH_SERVICE_URI
    path = '/auth/v1/userinfo'
    url = f'http://{auth_srv}{path}'
    data = orjson.dumps({'user_ids': [user_id]})
    headers = {'Authorization': settings.SECRET_KEY}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == HTTPStatus.OK:
        data = response.json()
        return data[0]

