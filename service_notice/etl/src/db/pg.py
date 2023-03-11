import logging

import psycopg2
from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import DictCursor

INIT_QUERY = """
CREATE TABLE IF NOT EXISTS template (
    id VARCHAR(255) PRIMARY KEY,
    template_text TEXT NOT NULL);
INSERT INTO template (id, template_text) VALUES('default','Привет, {{username}}. Ты получаешь {{present}}!')
ON CONFLICT (id) DO UPDATE
    SET template_text = EXCLUDED.template_text;
"""


class PostgresDB:
    def __init__(self, uri: str):
        logging.debug("start PostgreSQL")
        self.connection: PGConnection = psycopg2.connect(uri, cursor_factory=DictCursor)
        with self.connection.cursor() as cursor:
            cursor.execute(INIT_QUERY)
            logging.debug("init tables")
        self.connection.commit()

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
        return ""
