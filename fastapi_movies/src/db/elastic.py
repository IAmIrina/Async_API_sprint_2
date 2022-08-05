"""Implement search in ES."""

from typing import List, Tuple
from elasticsearch import NotFoundError
from models.custom_models import SortModel


from db.search import AsyncSearchEngine, BaseSearchAdapter


class ESAdapter(BaseSearchAdapter):
    """Implement search interface."""

    FUZZINESS = 'AUTO'

    def __init__(self, elastic: AsyncSearchEngine, index: str) -> None:
        self.client = elastic
        self.index = index

    async def fetch_one(self, uuid: str) -> dict:
        """Fetch document from ES Index by id.

        Args:
            uuid: Document id in ES.
        """
        try:
            doc = await self.client.get(index=self.index, id=uuid)
        except NotFoundError:
            return {}
        return doc['_source']

    async def full_text_search(
        self,
        query: dict,
        fields: List[str],
        from_: int = 0,
        size: int = 20,
    ) -> Tuple[List[dict], int]:
        """Full text search many from ES by query.

        Args:
            query: Search string.
            fields: Fields where to search for the query.
            from_: Start from the document.
            size: Page size.

        Returns:
            Tuple[List[dict], int] - Documents and their count.
        """
        es_query = {
            "multi_match": {
                "fuzziness": self.FUZZINESS,
                "operator": "or",
                "query": query,
                "fields": fields
            }
        }

        try:
            docs = await self.client.search(
                index=self.index,
                query=es_query,
                from_=from_,
                size=size
            )
        except NotFoundError:
            return [], 0

        return await self._parse_search_result(docs)

    async def fetch_all(
        self,
        from_: int = 0,
        size: int = 20,
        sort: SortModel = None,
    ) -> Tuple[List[dict], int]:
        """Fetch all from ES.

        Args:
            from_: Start from the document.
            size: Page size.
            sort: Field and order.

        Returns:
            Tuple[List[dict], int] - Documents and their count.

        """
        sort = await self._format_sort(sort)
        es_query = {"match_all": {}}
        docs = await self._fetch_many(
            query=es_query,
            from_=from_,
            size=size,
            sort=sort,
        )
        return await self._parse_search_result(docs)

    async def exact_search_in_one_field(
        self,
        value: dict,
        field: List[str],
        from_: int = 0,
        size: int = 20,
        sort: SortModel = None,
        _source: bool = True,
    ) -> Tuple[List[dict], int]:
        """Search records that cointains value in nested field.

        Args:
            value: Search value.
            field: Field where to search for the query.
            from_: Start from the document.
            size: Page size.
            sort: Sort: Field and order.
            _source: True to return documents else to return only uuids.

        Returns:
            Tuple[List[dict], int] - Documents and their count.

        """
        sort = await self._format_sort(sort)
        nested = field.split('.')
        es_query = {
            'nested': {
                'path': nested[0],
                'query': {
                    'bool': {
                        'must': [
                            {'match': {field: value}},
                        ]
                    }
                }
            }
        }
        docs = await self._fetch_many(
            query=es_query,
            from_=from_,
            size=size,
            sort=sort,
        )
        return await self._parse_search_result(docs, _source=_source)

    async def exact_search_in_many_fields(
        self,
        value: dict,
        fields: List[str],
        from_: int = 0,
        size: int = 20,
        sort: SortModel = None,
        _source: bool = True,
    ) -> Tuple[List[dict], int]:
        """Search records that cointains value in nested multyple fields.

        Args:
            value: Search value.
            field: Field where to search for the query.
            from_: Start from the document.
            size: Page size.
            sort: Sort: Field and order.
            _source: True to return documents else to return only uuids.

        Returns:
            Tuple[List[dict], int] - Documents and their count.

        """
        sort = await self._format_sort(sort)
        es_query = {"bool": {"boost": 1.0, "minimum_should_match": 1, "should": []}}
        for field in fields:
            nested = field.split('.')
            es_query['bool']['should'].append({
                "nested": {
                    "path": f'{nested[0]}', "query": {
                        "term": {
                            field: value
                        }
                    }
                }
            })
        docs = await self._fetch_many(
            query=es_query,
            from_=from_,
            size=size,
            sort=sort,
        )
        return await self._parse_search_result(docs, _source=_source)

    async def _fetch_many(self, **kwargs) -> dict:
        """Fetch many from ES by query.

        Args:
            index:
            kwargs: requests parameters.
        Returns:
            Tuple[List[dict], int] - Documents and their count.
        """
        try:
            docs = await self.client.search(
                index=self.index,
                **kwargs,
            )
        except NotFoundError:
            return [], 0

        return docs

    async def _parse_search_result(self, es_response, _source: bool = True):
        """Get documents from ES response and their count.

        Args:
            es_response: ES response.
            _source: True list of documents will be gotten otherwise list of documents uuids.

        Returns:
            Tuple[List[dict], int] - Documents and their count.

        """
        hits = es_response.get('hits')
        if not hits:
            return [], 0

        total = es_response['hits']['total']['value']
        if _source:
            docs = [doc['_source'] for doc in hits.get('hits', [])]
        else:
            docs = [doc['_id'] for doc in hits.get('hits', [])]

        return docs, total

    async def _format_sort(self, sort: SortModel) -> dict:
        """Create sort ES format dict."""
        if sort:
            return [{sort.field: {'order': sort.order}}, '_score']
        return {}


async def get_search_adapter() -> BaseSearchAdapter:
    """Return ESAdapter class."""
    return ESAdapter
