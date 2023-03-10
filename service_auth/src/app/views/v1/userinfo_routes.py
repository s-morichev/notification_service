from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.core.utils import error, jwt_accept_roles, validate_uuids
from app.services import user_service

userinfo_bp = Blueprint("userinfo", __name__)


@userinfo_bp.post("/userinfo")
@jwt_accept_roles("admin")
@jwt_required()
def get_users_info():
    user_ids = request.json.get("user_ids", None)

    if user_ids is None:
        return error("No ids provided", HTTPStatus.BAD_REQUEST)

    if not isinstance(user_ids, list):
        return error("Ids must be provided as list", HTTPStatus.BAD_REQUEST)

    validate_uuids(*user_ids)

    users_info = user_service.get_users_info(user_ids)
    response = jsonify(users_info=users_info)
    return response
