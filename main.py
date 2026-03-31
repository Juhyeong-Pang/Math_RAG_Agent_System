import logging
import os
import sys

from fastapi import FastAPI, UploadFile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent import RAGAgent
from src.utils.solve_question import (
    EvalResult,
    run_baseline_evaluation,
    run_full_evaluation,
)

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

agent = RAGAgent()


@app.post("/inference")
async def inference(file: UploadFile) -> EvalResult:
    result = await run_full_evaluation(file, agent)
    return result


@app.post("/inference-baseline")
async def baseline_inference(file: UploadFile) -> EvalResult:
    result = await run_baseline_evaluation(file, agent)
    return result


@app.post("/single-inference")
async def single_inference(request: str) -> str:
    predicted_answer = await agent.solve(request)

    return predicted_answer
