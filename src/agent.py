import asyncio
import json
import os
import re
import sys
from typing import Any  # , Literal, cast

from openai import AsyncOpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.collection import get_collection
from src.prompts import (
    BASELINE_SYSTEM_MSG,
    EXPLANATION_SYSTEM_MSG,
    FINAL_ANSWER_SYSTEM_MSG,
)
from src.utils.bm25_utils import BM25Data, load_bm25_index, tokenize_latex


class RAGAgent:
    def __init__(self):
        self.collection = get_collection()
        self.semaphore = asyncio.Semaphore(5)
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.bm25_data: BM25Data | None = load_bm25_index(
            os.path.join("search_db", "bm25_index.pkl")
        )

    async def solve(self, query: str) -> str:
        """The whole pipeline of RAG"""

        try:
            context = await self._retrieve_and_filter(query)
            result_json = await self._generate_final_response(query, context)

            return result_json.get("answer", "0")
        except Exception as e:
            print(f"Error When Retreiving Answer: {e}")
            return "0"

    async def _generate_final_response(self, query_extracted: str, context: str) -> str:
        """Method to create prompt and retrieve answer from the model"""
        system_msg = FINAL_ANSWER_SYSTEM_MSG

        prompt = (
            f"{context}\n\n"
            "\nSolve the following question Based on the related problems above:\n\n"
            f"Question:\n{query_extracted}\n\n"
            "Answer:"
        )

        # print(prompt)

        async with self.semaphore:
            response: Any = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )

        if not response.choices:
            raise ValueError("No choices returned from LLM")

        first_choice = response.choices[0]
        message = first_choice.message
        raw_content = message.content

        if raw_content is None:
            raise ValueError("LLM Response is empty")

        result = self._safe_json_load(raw_content)
        return re.sub(r"[\\]", "", result)

    def _safe_json_load(self, raw_content: str) -> dict:
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            try:
                fixed_content = raw_content.replace("\\", "\\\\")
                fixed_content = fixed_content.replace("\\\\\\\\", "\\\\")
                return json.loads(fixed_content)
            except Exception:
                match = re.search(r"\{.*\}", raw_content, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group())
                    except Exception:
                        pass

        return {"answer": "0", "error": "json_parse_failed"}

    async def _retrieve_and_filter(self, query: str) -> str:
        """Method to retrieve similar questions based on the distance"""
        results = self.collection.query(
            query_texts=[query],
            n_results=5,
        )

        documents_list = results.get("documents", [[]])
        ids_list = results.get("ids", [[]])
        distance_list = results.get("distances", [[]])

        v_docs: Any = []
        v_ids: Any = []

        if documents_list and ids_list and distance_list:
            v_docs = documents_list[0]
            v_ids = ids_list[0]
            # v_dists = distance_list[0]

        b_docs: list[Any] = []
        if self.bm25_data:
            bm25 = self.bm25_data["bm25"]
            all_docs = self.bm25_data["documents"]
            tokenized_query = tokenize_latex(query)

            b_docs = bm25.get_top_n(tokenized_query, all_docs, n=10)  # type: ignore

        k = 60
        scores: dict[str, float] = {}
        doc_map: dict[str, str] = {}

        for rank, (doc_id, doc) in enumerate(zip(v_ids, v_docs, strict=True)):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + k)
            doc_map[doc_id] = doc

        for rank, doc in enumerate(b_docs):
            doc_id = f"content_{hash(doc)}"
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + k)
            doc_map[doc_id] = doc

        reranked_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:5]

        context_parts: list[str] = []
        for i, doc_id in enumerate(reranked_ids):
            context_parts.append("-------")
            context_parts.append(f"Similar Question {i + 1}:\n{doc_map[doc_id]}")
            context_parts.append("-------")

        if not context_parts:
            return "This is a hard question. Please solve extra carefully."

        context = (
            "\n\n"
            "--- Start of Example Questions ---\n\n"
            + "\n\n".join(context_parts)
            + "\n\n--- End of Example Questions ---"
        )

        context_explained = await self._generate_explanation(context=context)

        final_context = f"{context}\n\nThis is the core concepts used for questions similar to the one you need to solve. Please refer to it if needed: \n{context_explained}"

        return final_context

    async def _generate_explanation(self, context: str) -> str:
        """Method that creates summary / explanation for the retrieved questions"""
        try:
            explanation_system_msg = EXPLANATION_SYSTEM_MSG

            async with self.semaphore:
                response: Any = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": explanation_system_msg},
                        {"role": "user", "content": f"Original Question: {context}"},
                    ],
                    temperature=0,
                    response_format={"type": "json_object"},
                )

            if not response.choices:
                raise ValueError("No choices returned from LLM")

            first_choice = response.choices[0]
            message = first_choice.message
            raw_content = message.content

            if raw_content:
                explanations = json.loads(raw_content)
                context_explained = "\n - ".join(explanations["Explanation"])
                return context_explained
        except Exception as e:
            print(f"Query Expansion Error: {e}")

        return context

    async def solve_baseline(self, query: str) -> str:
        """The whole pipeline of RAG"""

        try:
            system_msg = BASELINE_SYSTEM_MSG

            prompt = f"Question:\n{query}\n\nAnswer:"

            async with self.semaphore:
                response: Any = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0,
                    response_format={"type": "json_object"},
                )

            if not response.choices:
                raise ValueError("No choices returned from LLM")

            first_choice = response.choices[0]
            message = first_choice.message
            raw_content = message.content

            if raw_content is None:
                raise ValueError("LLM Response is empty")

            content: dict[str, Any] = json.loads(raw_content)

            return content.get("answer", "0")
        except Exception as e:
            print(f"Error When Retreiving Answer: {e}")
            return "0"

    def get_semaphore(self):
        return self.semaphore


if __name__ == "__main__":
    question = r"I want to read 4 books over the next month.  My bookshelf has 12 different books.  In how many ways can I choose which books to read over the next month, without regard to the order that I read them?"

    agent = RAGAgent()
    answer = asyncio.run(agent.solve(question))
    print(f"Answer: {answer}")
