# flask_app/db_models.py
import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

    def __repr__(self):
        return f"<User {self.login}>"

    @classmethod
    def find_by_email(cls, email):
        query = cls.query.filter_by(email=email).first()
        return query
