"""Transform data process."""

import logging
from logging.config import dictConfig
from typing import Callable

from pydantic import BaseModel

from lib.loggers import LOGGING
from lib import schemas, storage

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Transformer(object):
    """Implement transform data to Elasticksearch index schema format.

    Transform income data using pydantic schema.

    Attributes:
        result_handler: Result of proccessing will return to the callable.
        storage: Permanent storage to keep state.
        state: State of the process

    """

    def __init__(
        self,
        schema: BaseModel,
        redis_settings: dict,
        result_handler: Callable,
    ) -> None:
        """Transformer class constructor.

        Args:
            schema: Pydentic validation schema
            result_handler: Result of the proccessing will be returned to the function.
            redis_settings: Redis connection settings.

        """

        self.schema = schema
        self.storage = storage.RedisStorage(redis_settings)
        self.state = storage.State(self.storage)
        self.result_handler = result_handler
        self.proceed()

    def proceed(self) -> None:
        """Check the state and proceed to work if there is data in the cashe."""

        if self.state.state.get('data'):
            logger.debug('Data to proceed %s', self.state.state.get('data'))
            self.proccess(
                movies=self.state.state.get('data'),
            )

    def set_state(self, **kwargs) -> None:
        """Set State in cache.

        Args:
            kwargs: Key/value pair to save in cache.

        """
        for key, value in kwargs.items():
            self.state.set_state(key=key, value=value)

    def proccess(self, records: list) -> None:
        """Transform data and pass results to result_handler.

        Args:
            records: movies data to transform.

        """
        self.set_state(data=list(records))
        for idx, record in enumerate(records):
            try:
                records[idx] = self.schema(**record).dict(by_alias=True)
            except Exception:
                logger.exception('Validation data error: %s', records[idx])
        self.set_state(data=None)
        self.result_handler(records)


class MovieTransformer(Transformer):
    """Special logic to transform movie instance."""

    def get_person_names(self, persons: dict, played_roles: list = None) -> str:
        """Get list of persons names.

        Args:
            persons: List of Persons to extract names
            played_roles: List of Roles to filter.

        """
        if played_roles:
            return [person['name'] for person in persons if person['role'] in played_roles]
        return [person['name'] for person in persons]

    def persons_by_role(self, persons: dict, played_roles: list = None) -> dict:
        """Get list of persons info.

        Args:
            persons: List of Persons to extract names
            played_roles: List of Roles to filter.

        """
        if played_roles:
            return [schemas.Person(**person).dict() for person in persons if person['role'] in played_roles]
        return [schemas.Person(**person).dict() for person in persons]

    def proccess(self, movies: list) -> None:
        """Transform movies data and pass results to result_handler.

        Args:
            movies: movies data to transform.

        """
        self.set_state(data=list(movies))
        for idx, movie in enumerate(movies):
            persons = movie['persons']
            try:
                movies[idx] = self.schema(
                    **movies[idx],
                    director=self.get_person_names(persons, ['director']),
                    actors_names=self.get_person_names(persons, ['actor']),
                    writers_names=self.get_person_names(persons, ['writer']),
                    directors=self.persons_by_role(persons, ['director']),
                    actors=self.persons_by_role(persons, ['actor']),
                    writers=self.persons_by_role(persons, ['writer']),
                ).dict(by_alias=True)
            except Exception:
                logger.exception('Validation data error: %s', movies[idx])
        self.set_state(data=None)
        self.result_handler(movies)
