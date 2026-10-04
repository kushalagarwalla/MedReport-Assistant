from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "text-embedding-3-large"
    llm_model: str = "gpt-6-luna"
    reasoning_effort: str = "low"
    top_k: int = 4


settings = Settings()
