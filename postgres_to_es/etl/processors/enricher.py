"""Enrich data process."""

import logging
from logging.config import dictConfig
from typing import Callable, List

from lib.loggers import LOGGING
from database.pg_database import PGConnection
from lib import storage
from psycopg2.sql import SQL

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Enricher(object):
    """Implement getting additional information about movies.

    Attributes:
        pg: Used to work with PG Database.
        result_handler: Result of proccessing will return to the callable.
        storage: Permanent storage to keep state.
        state: State of the process
        page_size: Count of records to return.

    """

    def __init__(self,
                 pg: PGConnection,
                 redis_settings: dict,
                 sql_template: str,
                 result_handler: Callable,
                 ) -> None:
        """Enricher class constructor.

        Args:
            pg: Used to work with PG Database.
            result_handler: Result of the proccessing will return to the function.
            redis_settings: Redis connection settings.
            sql_template: SQL to execute.

        """
        self.pg = pg
        self.result_handler = result_handler
        self.storage = storage.RedisStorage(redis_settings)
        self.state = storage.State(self.storage)
        self.cache_key = storage.get_md5(sql=sql_template)
        self.sql = SQL(sql_template)
        self.proceed()

    def proceed(self) -> None:
        """Check the state and proceed to work if there is data in the cashe."""
        if self.state.state.get(self.cache_key):
            logger.debug('Data in cache to proceed %s', self.state.state.get(self.cache_key))
            self.proccess(
                self.state.state[self.cache_key],
            )

    def proccess(self, records: List[dict]) -> None:
        """Run sql to enrich data and pass results to result_handler.

        Args:
            records: Recods list to enrich.

        """
        logger.debug('Enticher in proccess')
        self.state.set_state(key=self.cache_key, value=records)

        query_result = self.pg.retry_fetchall(
            self.sql,
            pkeys=tuple({record.get('uuid') for record in records}),
        )

        self.state.set_state(key=self.cache_key, value=None)

        if query_result:
            logger.debug('Got additional info for %s  movies', len(query_result))
            self.result_handler(query_result)
