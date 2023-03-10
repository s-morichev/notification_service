from uuid import UUID
import logging

import redis

from core.constants import Mark


class Storage:
    redis: redis.Redis

    def __init__(self, uri: str):
        logging.debug('start Redis')
        self.redis = redis.from_url(uri)

    @staticmethod
    def mark_key(notice_id: UUID, user_id: UUID) -> str:
        return f"notice:{notice_id}:user:{user_id}"

    def mark_processed(self, notice_id: UUID, user_id: UUID, result=Mark.QUEUED, ttl=24 * 60 * 60):
        key = self.mark_key(notice_id, user_id)
        self.redis.set(key, result.value, ex=ttl)
        logging.debug("marked notice:{0} user:{1} mark:{2}".format(notice_id, user_id, result.name))

    def get_mark(self, notice_id: UUID, user_id: UUID) -> Mark | None:
        key = self.mark_key(notice_id, user_id)
        value = self.redis.get(key)
        if not value:
            return None

        value = int(value.decode("utf-8"))
        return Mark(value)

    def close(self):
        if self.redis:
            self.redis.close()
            logging.debug('close Redis')


db: Storage | None = None


def set_mark(notice_id, user_id, result=Mark.QUEUED, ttl=24 * 60 * 60):
    if db:
        db.mark_processed(notice_id, user_id, result, ttl)


def get_mark(notice_id: UUID, user_id: UUID) -> Mark | None:
    if db:
        return db.get_mark(notice_id, user_id)
    else:
        return None

