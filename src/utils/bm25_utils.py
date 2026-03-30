import os
import pickle
import re
from typing import TypedDict, cast

from rank_bm25 import BM25Okapi


class BM25Data(TypedDict):
    bm25: BM25Okapi
    documents: list[str]


def tokenize_latex(text: str) -> list[str]:
    if not text:
        return []

    text = text.replace("\\", " ")

    text = re.sub(r"[\{\}\[\]\(\)\+\-\*\/\=\^\_\!\%\&\,\.\:]", " ", text)

    tokens = re.findall(r"\w+", text.lower())
    return tokens


def save_bm25_index(documents: list[str], save_path: str):
    if not documents:
        print("Error: No documents to index.")
        return

    print(f"Start Indexing... (total: {len(documents)})")

    tokenized_corpus = [tokenize_latex(doc) for doc in documents]

    bm25 = BM25Okapi(tokenized_corpus)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    data_to_save: BM25Data = {"bm25": bm25, "documents": documents}

    with open(save_path, "wb") as f:
        pickle.dump(data_to_save, f)

    print(f"Index Saved To: {save_path}")


def load_bm25_index(path: str) -> BM25Data | None:
    if not os.path.exists(path):
        print(f"Warning: File not found at {path}")
        return None

    with open(path, "rb") as f:
        return cast(BM25Data, pickle.load(f))
