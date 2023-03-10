import logging

import psycopg2
from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import DictCursor


class PostgresDB:
    def __init__(self, uri: str):
        logging.debug("start PostgreSQL")
        self.connection: PGConnection = psycopg2.connect(uri, cursor_factory=DictCursor)

    def execute_query(self, query: str) -> list[tuple]:
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result

    def close(self):
        if self.connection:
            self.connection.close()
            logging.debug("close PostgreSQL")


db: PostgresDB | None = None


def get_template_from_db(template_id: str) -> str:
    query = "select template_text from template where id='{0}'"
    result = db.execute_query(query.format(template_id))
    if result:
        return result[0][0]
    else:
        return ''
