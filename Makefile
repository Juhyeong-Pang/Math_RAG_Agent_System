SHELL = bash
ifneq ("$(wildcard .env)","")
	include .env
endif

ifeq ($(OS),Windows_NT)
    OPEN_CMD := start
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        OPEN_CMD := open
    else
        OPEN_CMD := xdg-open
    endif
endif

launch:
	docker build -t rag-math .
	(sleep 8 && $(OPEN_CMD) http://localhost:8000/docs) &
	docker run -p 8000:8000 --env-file .env rag-math

ingestion:
	uv run python scripts/run_ingestion.py

# This will push all commits to remote.
README:
	git add README.md
	git commit -m "Update README.md"
	git push
