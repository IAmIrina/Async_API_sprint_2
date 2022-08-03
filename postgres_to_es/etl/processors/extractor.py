"""Extract data from source."""

import datetime
import logging
from logging.config import dictConfig
from typing import Callable

from lib.loggers import LOGGING
from database.pg_database import PGConnection
from lib import storage
from psycopg2.sql import SQL

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Extractor(object):
    """Extract data from PostgreSQL database.

    Attributes:
        pg: Used to work with PG Database.
        result_handler: Result of proccessing will return to the callable.
        storage: Permanent storage to keep state.
        state: State of the process.

    """

    def __init__(
        self,
        pg: PGConnection,
        redis_settings: dict,
        sql_template: str,
        result_handler: Callable,
        page_size: int = 100,
    ) -> None:
        """Extractor class constructor.

        Args:
            pg: Used to work with PG Database.
            result_handler: Result of proccessing will return to the function.
            redis_settings: Redis connection settings.
            sql_template: SQL to execute.
            page_size: Limit for SQL.

        """
        self.pg = pg
        self.result_handler = result_handler
        self.storage = storage.RedisStorage(redis_settings)
        self.state = storage.State(self.storage)
        self.cache_key = storage.get_md5(sql=sql_template)
        self.sql = SQL(sql_template)
        self.page_size = page_size

    def get_last_modified(self, key: str) -> str:
        """Get last id from cache.

        Args:
            key: Cashe key to get data from cache.

        Returns:
            str: ISO format date.
        """
        modified = self.state.get_state(key)
        return modified or datetime.date.min

    def proccess(self) -> None:
        """Get modified data."""
        logger.debug('Extract modified records.')

        query_result = self.pg.retry_fetchall(
            self.sql,
            modified=self.get_last_modified(self.cache_key),
            page_size=self.page_size,
        )

        logger.debug('Got %s records.', len(query_result))
        if query_result:
            self.state.set_state(key=self.cache_key, value=query_result[-1]['modified'])

            self.result_handler(records=query_result)
