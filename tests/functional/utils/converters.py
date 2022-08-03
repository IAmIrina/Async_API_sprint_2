async def to_es_bulk_format(index: str, docs: list) -> list:
    bulk = []
    for doc in docs:
        bulk.append(
            {
                "index":
                {
                    "_index": index,
                    "_id": doc['uuid']
                }
            }
        )
        bulk.append(doc)
    return bulk
