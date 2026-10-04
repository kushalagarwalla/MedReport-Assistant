from langchain.tools import tool
from langchain_core.vectorstores import VectorStore


def make_report_tool(vector_store: VectorStore, k: int = 4):
    @tool
    def get_report_context(query: str) -> str:
        """
        Search the user's uploaded lab report and return the passages most relevant to the query
        """
        results = vector_store.similarity_search(query=query, k=k)
        return "\n\n".join(doc.page_content for doc in results)

    return get_report_context
