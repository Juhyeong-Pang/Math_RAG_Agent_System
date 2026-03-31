ingestion:
	uv run python scripts/run_ingestion.py

# This will push all commits to remote.
README:
	git add README.md
	git commit -m "Update README.md"
	git push

launch:
	docker build -t rag-math .
	(sleep 5 && $(OPEN_CMD) http://localhost:8000/docs) &
	docker run -p 8000:8000 --env-file .env rag-math