# flask_app/db.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import redis

DB_URI = "postgresql://app:123qwe@localhost/movies_database"

db = SQLAlchemy()
redis_db = redis.Redis(host="localhost", password="123qwe", port=6379, db=0)


def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    # db.metadata.schema = 'auth'
    db.init_app(app)
    app.app_context().push()
    db.create_all()


def set_token(user_id, device_id, token, expires):
    key = f"{user_id}#{device_id}"
    print(key)
    redis_db.set(name=key, value=token, ex=expires)


def check_token(user_id, device_id, token):
    key = f"{user_id}#{device_id}"
    print(key)
    value = redis_db.get(key).decode("utf-8")
    result = value and (value == token)
    if not result:
        print(f"{token}")
        print(f"{value}")

    return result
