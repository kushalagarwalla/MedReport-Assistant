from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore, VectorStore
from langchain_openai import OpenAIEmbeddings


def build_vector_store(docs: list[Document], embedding_model: str) -> VectorStore:
    embeddings = OpenAIEmbeddings(model=embedding_model)
    return InMemoryVectorStore.from_documents(docs, embeddings)
