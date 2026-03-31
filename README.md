# RAG Agent System for Solving Math Problems

## Description

**Objective**: The core motivation for this project is to implement an RAG Agent System that helps LLM Models answer math question written in latex format.

**Key Achievement**: Improved GPT-o4-mini's performance by {}%.

**File Structure**:

```plain text
RAG_Math
 ┣ data
 ┃ ┣ test_with_answer.csv
 ┃ ┗ train.csv
 ┣ search_db
 ┃ ┣ vector_db
 ┃ ┗ bm25_index.pkl
 ┣ scripts
 ┃ ┣ append_answer.py
 ┃ ┗ run_ingestion.py
 ┣ src
 ┃ ┣ utils
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┗ bm25_utils.cpython-312.pyc
 ┃ ┃ ┣ bm25_utils.py
 ┃ ┃ ┗ solve_question.py
 ┃ ┣ agent.py
 ┃ ┣ collection.py
 ┃ ┗ prompts.py
 ┣ .env
 ┣ pyproject.toml
 ┣ Dockerfile
 ┣ Makefile
 ┣ uv.lock
 ┣ README.md
 ┗ main.py
```

## Quick Start

Enter your Open AI API key first, then call `make launch`. It might take a while for this program to start.

```bash
echo "OPENAI_API_KEY=your_api_key" > .env

make launch
```

Try the `/inference` endpoint by putting in the `test_with_answer.csv` file. You can try with any csv file, but it must have the same columns as the `test_with_answer.csv`.
