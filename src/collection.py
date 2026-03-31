import os
import sys
from typing import cast

import chromadb
from chromadb.api.types import Embeddable, EmbeddingFunction
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_collection(name: str = "qa_collection"):
    api_key = os.getenv("OPENAI_API_KEY")
    db_path = os.getenv("DB_PATH", os.path.join("search_db", "/vector_db"))

    client = chromadb.PersistentClient(path=db_path)

    openai_ef = OpenAIEmbeddingFunction(
        api_key=api_key, model_name="text-embedding-3-small"
    )

    return client.get_or_create_collection(
        name=name,
        embedding_function=cast(EmbeddingFunction[Embeddable], openai_ef),
        metadata={"hnsw:space": "cosine"},
    )
