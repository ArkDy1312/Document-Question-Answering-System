# Run all unit tests
test:
	pytest tests/

# Run a specific test file
test-file:
	pytest $(f)

# Format code with black
format:
	black app/ tests/ main.py

# Run the full Stage 1 ingestion pipeline (manual test)
run:
	python main.py

# Setup environment (virtualenv + install deps)
init:
	python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
