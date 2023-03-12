import logging
from http import HTTPStatus
from uuid import UUID

import orjson
import requests
from requests.exceptions import RequestException

from core.config import settings
from core.models import UserInfo


def get_user_info_from_auth(request_id: str, user_id: UUID) -> UserInfo | None:
    auth_srv = settings.AUTH_SERVICE_URI
    path = "/auth/v1/userinfo"
    url = f"http://{auth_srv}{path}"
    data = orjson.dumps({"user_ids": [user_id]})
    headers = {"Authorization": settings.SECRET_KEY, "X-Request-Id": request_id, "Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=data)

    except RequestException as err:
        logging.error(f'error call auth service. Error: {err}')

    else:
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            if data and "users_info" in data:
                users_info = data["users_info"]
                if len(users_info) > 0:
                    return UserInfo(**users_info[0])

    return None


def get_users_info_from_auth(request_id: str, user_ids: list[UUID]) -> dict[UUID, UserInfo]:
    auth_srv = settings.AUTH_SERVICE_URI
    path = "/auth/v1/userinfo"
    url = f"http://{auth_srv}{path}"
    data = orjson.dumps({"user_ids": user_ids})
    headers = {"Authorization": settings.SECRET_KEY, "X-Request-Id": request_id, "Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=data)

    except RequestException as err:
        logging.error(f'error call auth service. Error: {err}')

    else:
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            if data and "users_info" in data:
                users_info = data["users_info"]
                result = {item['user_id']: UserInfo(**item) for item in users_info}
                return result

    return {}
