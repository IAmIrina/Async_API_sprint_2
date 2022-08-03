"""Movies ETL Service."""

import logging
from logging.config import dictConfig
from time import sleep

from lib.loggers import LOGGING
from config import settings
import flows

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == '__main__':

    logger.info('Started')
    workflows = (
        flows.etl_movies_by_person(),
        flows.etl_movies_by_genre(),
        flows.etl_modified_movies(),
        flows.etl_genres(),
        flows.etl_persons(),
    )

    while True:
        for workflow in workflows:
            workflow.proccess()
            sleep(settings.delay)
