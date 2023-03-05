# flask_api/db_models.py
import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from db import db


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    def to_dict(self):
        return {"id": self.id, "login": self.login, "password": self.password}

    def __repr__(self):
        return f"<User {self.name}>"

    @classmethod
    def find_by_email(cls, email):
        query = cls.query.filter_by(email=email).first()
        return query
