from langchain.agents import create_agent
from langchain_core.vectorstores import VectorStore
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from medreport.config import settings
from medreport.prompts import SYSTEM_PROMPT
from medreport.tools import make_report_tool


def build_agent(vector_store: VectorStore):
    llm = ChatOpenAI(model=settings.llm_model, reasoning_effort=settings.reasoning_effort)
    return create_agent(
        model=llm,
        tools=[make_report_tool(vector_store, k=settings.top_k)],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )
