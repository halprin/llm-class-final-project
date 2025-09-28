import itertools
import os
import uuid

import iterator_chain
from pinecone import Pinecone, IndexEmbed


class Database:
    def __init__(self):
        index_name = "diary2"
        self._namespace = "diary"
        self._pinecone = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

        if not self._pinecone.has_index(index_name):
            self._pinecone.create_index_for_model(
                name=index_name,
                cloud="aws",
                region="us-east-1",
                embed=IndexEmbed(
                    model="llama-text-embed-v2",
                    field_map={"text": "text"},
                    metric="cosine",
                    read_parameters={"input_type": "query", "truncate": "NONE"},
                    write_parameters={"input_type": "passage", "truncate": "NONE"},
                ),
            )
        self._index = self._pinecone.Index(index_name)

    def add_documents(self, documents: list[dict[str, str]]):
        documents = (
            iterator_chain.from_iterable(documents)
            .map(lambda document: {**document, "_id": str(uuid.uuid4())})
            .list()
        )

        for documents_chunk in self._chunks(documents):
            self._index.upsert_records(self._namespace, documents_chunk)

    def retrieve_documents(self, query: str) -> list[dict[str, str]]:
        results = self._index.search(
            namespace=self._namespace,
            query={"top_k": 10, "inputs": {"text": query}},
            fields=["*"],
            rerank={
                "model": "bge-reranker-v2-m3",
                "top_n": 5,
                "rank_fields": ["text"],
            },
        )

        return results["result"]["hits"]

    def has_data(self) -> bool:
        return self._index.describe_index_stats()["total_vector_count"] > 0

    def _chunks(self, iterable, batch_size=96):
        """A helper function to break an iterable into chunks of size batch_size."""
        it = iter(iterable)
        chunk = list(itertools.islice(it, batch_size))
        while chunk:
            yield chunk
            chunk = list(itertools.islice(it, batch_size))
