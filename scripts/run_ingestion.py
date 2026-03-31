import asyncio
import hashlib
import logging
import os
import sys

import pandas as pd
from chromadb.api.types import Metadata
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.collection import get_collection
from src.utils.bm25_utils import save_bm25_index

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_id_from_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


async def run_ingestion():
    df = pd.read_csv(os.path.join("data", "train.csv"))

    collection = get_collection()

    documents = []
    metadatas = []
    ids = []

    documents: list[str] = [
        f"Question:\n{question}\n\nSolution:\n{solution}".strip()
        for question, solution in zip(
            df["problem"],
            df["solution"],
            strict=True,
        )
    ]

    metadatas: list[Metadata] = [
        {
            "Level": level,
            "Category": type,
        }
        for level, type in zip(df["level"], df["type"], strict=True)
    ]

    ids = [generate_id_from_text(doc) for doc in documents]

    batch_size = 100
    for i in range(0, len(documents), batch_size):
        try:
            collection.upsert(
                ids=ids[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )
            logging.info(f"Batch {i // batch_size + 1} indexed.")
        except Exception as e:
            logging.error(f"Failed to index batch at {i}: {e}")
    print(f"Successfully indexed {len(documents)} items.")

    bm25_path = os.path.join("bm25_index.pkl")
    save_bm25_index(documents, bm25_path)


if __name__ == "__main__":
    asyncio.run(run_ingestion())
