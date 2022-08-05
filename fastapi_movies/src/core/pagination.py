"""Implement Paginator class"""
import math
from typing import Any

from models.custom_models import PaginationModel


class Paginator():

    def __init__(self, model: PaginationModel):
        self.model = model

    async def paginate(self, data: Any, page_num: int, page_size: int, total_count: int) -> PaginationModel:
        """ Move to paginate structure """

        total_pages = math.ceil(total_count / page_size)
        return self.model(
            total_pages=total_pages,
            page_num=page_num,
            page_size=page_size,
            data=data
        )
