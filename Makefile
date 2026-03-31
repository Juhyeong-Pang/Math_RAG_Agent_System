ingestion:
	uv run python src/scripts/run_ingestion.py

# This will push all commits to remote.
README:
	git add README.md
	git commit -m "Update README.md"
	git push
