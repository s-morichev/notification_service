# flask_app/app.py
import hashlib
from datetime import timedelta
from http import HTTPStatus as status

from db_models import User
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_csrf_token,
    get_jwt,
    get_jwt_identity,
    get_unverified_jwt_headers,
    jwt_required,
    set_refresh_cookies,
)

from db import check_token, db, init_db, set_token

# from jwt import

app = Flask(__name__)


count = 0


@app.route("/")
def default():
    global count
    count += 1
    user = User(login=f"user {count}", password="123")

    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    return response


@app.route("/ping", methods=["GET", "POST"])
# @app.route('/ping', methods=['GET'])
def ping():
    content = request.json
    value = content["load"]
    # value = 'aa'
    return jsonify({"load": value, "result": str(value).upper(), "agent": str(request.user_agent)})


def get_auth_user(email, password):
    user = User.find_by_email(email)
    # todo: hash password!!!
    if user and (user.password == password):
        return user
    else:
        return None


@app.route("/login", methods=["POST"])
def login():
    content = request.json
    if "email" in content and "password" in content:
        email = content["email"]
        password = content["password"]

        user = get_auth_user(email, password)
        if user:
            u_a = str(request.user_agent)
            print(f"user_id:{user.id}")
            device_id = hashlib.sha1(u_a.encode("utf-8")).hexdigest()

            ext_claims = {"name": user.name, "role": ["user"], "device_id": device_id}

            access_token = create_access_token(identity="user.id", additional_claims=ext_claims, fresh=True)
            refresh_token = create_refresh_token(identity="user.id", additional_claims=ext_claims)
            token = decode_token(refresh_token)
            set_token(user.id, device_id, str(token), token["exp"])
            # csrf = get_csrf_token()
            response = jsonify(access_token=access_token, refresh_token=refresh_token)

            set_refresh_cookies(response, refresh_token)

            return response

            # payload = {'access_token': access_token}
            # response = jsonify(payload)
            # response.status = status.OK
        else:
            payload = {"error": "user not fount"}
            response = jsonify(payload)
            response.status = status.NOT_FOUND
    else:
        response = jsonify({"error": "no login and/or password data"})
        response.status = status.BAD_REQUEST

    return response


@app.route("/refresh", methods=["GET", "POST"])
@jwt_required(refresh=True)
# @jwt_required(verify_type=False)
def refresh():
    """в запросе надо устанавливать X-Csrf-Token, брать его из refresh_token, они разные!"""
    # identity = get_jwt_identity()
    jwt = get_jwt()

    # check_jwt_in_redis()
    #  как получить digest tokena? или сырой токен?
    if not check_token(jwt["sub"], jwt["device_id"], str(jwt)):
        return jsonify({"msg": "error"}), 403

    print(jwt)
    # копируем данные из токена
    ext_claims = {"name": jwt["name"], "role": jwt["role"], "device_id": jwt["device_id"]}

    access_token = create_access_token(identity=jwt["sub"], additional_claims=ext_claims, fresh=timedelta(minutes=15))
    refresh_token = create_refresh_token(identity=jwt["sub"], additional_claims=ext_claims)

    # set_redis_key
    token = decode_token(refresh_token)
    set_token(jwt["sub"], jwt["device_id"], str(token), token["exp"])

    response = jsonify(access_token=access_token, refresh_token=refresh_token)

    set_refresh_cookies(response, refresh_token)

    return response


@app.route("/secret", methods=["GET", "POST"])
@jwt_required()
def secret():
    return jsonify({"result": "the secret"})


def main():

    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "super-secret"

    app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]

    # иначе требует csrf token!
    # app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # If true this will only allow the cookies that contain your JWTs to be sent
    # over https. In production, this should always be set to True
    # что это значит????
    app.config["JWT_COOKIE_SECURE"] = False

    jwt = JWTManager(app)

    init_db(app)
    app.run(debug=True)


if __name__ == "__main__":
    main()
