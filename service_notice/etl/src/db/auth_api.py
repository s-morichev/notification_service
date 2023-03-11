from http import HTTPStatus
from uuid import UUID

import orjson
import requests

from core.config import settings
from core.models import UserInfo


def get_user_info_from_auth(request_id: str, user_id: UUID) -> UserInfo | None:
    auth_srv = settings.AUTH_SERVICE_URI
    path = "/auth/v1/userinfo"
    url = f"http://{auth_srv}{path}"
    data = orjson.dumps({"user_ids": [user_id]})
    headers = {"Authorization": settings.SECRET_KEY, "X-Request-Id": request_id, "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == HTTPStatus.OK:
        data = response.json()
        if data and "users_info" in data:
            users_info = data["users_info"]
            if len(users_info) > 0:
                return UserInfo(**users_info[0])

    return None
