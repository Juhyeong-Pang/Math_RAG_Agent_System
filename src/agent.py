import asyncio

# import json
import os
import sys

# from typing import Any, Literal, cast
from openai import AsyncOpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from src.prompts import FINAL_ANSWER_SYSTEM_MSG, EXPLANATION_SYSTEM_MSG
from src.collection import get_collection
from src.utils.bm25_utils import BM25Data, load_bm25_index


class RAGAgent:
    def __init__(self):
        self.collection = get_collection()
        self.semaphore = asyncio.Semaphore(5)
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.bm25_data: BM25Data | None = load_bm25_index("data/bm25_index.pkl")

    # solve -(calls)-> generate_final_response -(calls)-> _retrieve_and_filter -(calls)-> _generate_explanation

    async def solve(self, query: str) -> str:
        """The whole pipeline of RAG"""

        # return answer

    async def _generate_final_response(self, query_extracted: str, context: str) -> str:
        """Method to create prompt and retrieve answer from the model"""
        pass

    async def _retrieve_and_filter(self, query: str) -> str:
        """Method to retrieve similar questions based on the distance"""
        pass

    async def _generate_explanation(self, context: str) -> str:
        """Method that creates summary / explanation for the retrieved questions"""
        pass
