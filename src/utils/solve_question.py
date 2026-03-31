import asyncio
import os
import sys
import time
from typing import Any, cast

import pandas as pd
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from tqdm.asyncio import tqdm as asynctqdm

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.agent import RAGAgent

TEST_SIZE = 500


class EvalResult(BaseModel):
    accuracy: float
    time_taken: float
    total: int
    correct_count: int
    detail: list[dict[str, Any]]


async def solve_single_question(
    row: pd.Series, agent: RAGAgent, semaphore: asyncio.Semaphore
):
    async with semaphore:
        try:
            question = row["problem"]
            result = await asyncio.wait_for(agent.solve(question), timeout=90.0)
            answer = str(result)
            actual_answer = row["answer"]
            is_correct = answer == actual_answer
            query_dict = {
                "problem": question,
                "answer": answer,
                "actual_answer": actual_answer,
                "level": row["level"],
                "type": row["type"],
                "is_correct": is_correct,
            }

            return is_correct, query_dict
        except Exception as e:
            print(f"Error: {e}")
            return False, {"problem": row.get("problem", ""), "error": str(e)}


async def run_full_evaluation(file: UploadFile, agent: RAGAgent) -> EvalResult:
    start_time = time.time()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Start Evaluating...")

    try:
        df = pd.read_csv(file.file).sample(frac=1, random_state=42).head(TEST_SIZE)
        if "problem" not in df.columns or "answer" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="csv file must contain 'problem' and 'answer' columns",
            )

        semaphore = asyncio.Semaphore(15)

        tasks = [
            solve_single_question(row, agent, semaphore) for i, row in df.iterrows()
        ]

        all_results = await cast(
            Any,
            asynctqdm.gather(*tasks, desc="Evaluating in Parallel"),  # type: ignore
        )

        correct_count = sum(1 for is_correct, _ in all_results if is_correct)
        details = [detail for _, detail in all_results]

        duration = time.time() - start_time
        accuracy = correct_count / len(df) if len(df) > 0 else 0

        return EvalResult(
            accuracy=float(accuracy),
            time_taken=duration,
            total=len(df),
            correct_count=correct_count,
            detail=details,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {str(e)}") from e


async def solve_baseline_single_question(
    row: pd.Series, agent: RAGAgent, semaphore: asyncio.Semaphore
):
    async with semaphore:
        try:
            question = row["problem"]
            result = await asyncio.wait_for(
                agent.solve_baseline(question), timeout=90.0
            )
            answer = str(result)
            actual_answer = row["answer"]
            is_correct = answer == actual_answer
            query_dict = {
                "problem": question,
                "answer": answer,
                "actual_answer": actual_answer,
                "level": row["level"],
                "type": row["type"],
                "is_correct": is_correct,
            }

            return is_correct, query_dict
        except Exception as e:
            print(f"Error: {e}")
            return False, {"problem": row.get("problem", ""), "error": str(e)}


async def run_baseline_evaluation(file: UploadFile, agent: RAGAgent) -> EvalResult:
    start_time = time.time()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Start Evaluating...")

    try:
        df = pd.read_csv(file.file).sample(frac=1, random_state=42).head(TEST_SIZE)
        if "problem" not in df.columns or "answer" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="csv file must contain 'problem' and 'answer' columns",
            )

        semaphore = asyncio.Semaphore(15)

        tasks = [
            solve_baseline_single_question(row, agent, semaphore)
            for i, row in df.iterrows()
        ]

        all_results = await cast(
            Any,
            asynctqdm.gather(*tasks, desc="Evaluating in Parallel"),  # type: ignore
        )

        correct_count = sum(1 for is_correct, _ in all_results if is_correct)
        details = [detail for _, detail in all_results]

        duration = time.time() - start_time
        accuracy = correct_count / len(df) if len(df) > 0 else 0

        return EvalResult(
            accuracy=float(accuracy),
            time_taken=duration,
            total=len(df),
            correct_count=correct_count,
            detail=details,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {str(e)}") from e
