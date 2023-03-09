from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.core.utils import error, jwt_accept_roles
from app.services import user_service

userinfo_bp = Blueprint("userinfo", __name__)


@userinfo_bp.post("/userinfo")
@jwt_accept_roles("admin")
@jwt_required()
def get_users_info():
    user_uuids = request.json.get("user_uuids", None)

    if user_uuids is None:
        return error("No uuids provided", HTTPStatus.BAD_REQUEST)

    users_info = user_service.get_users_info(user_uuids)
    response = jsonify(users_info=users_info)
    return response
