import os

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec


class Database:
    def __init__(self):
        index_name = "diary"
        self._pinecone = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

        if not self._pinecone.has_index(index_name):
            self._pinecone.create_index(
                name=index_name,
                vector_type="dense",
                dimension=4096,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        self._index = self._pinecone.Index(index_name)
        self._embedder = OllamaEmbeddings(model="llama3.1:8b")
        self._store = PineconeVectorStore(embedding=self._embedder, index=self._index)

    def add_documents(self, documents: list[Document]):
        self._store.add_documents(documents)
