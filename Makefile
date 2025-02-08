.PHONY: format lint test setup clean

format:
	poetry run ruff format .
	poetry run ruff check --fix .

lint:
	poetry run pyright .
	poetry run ruff --check .
	poetry run pylint --check-only .

test:
	poetry run pytest

# Clean up the environment (delete virtual environment and requirements.txt)
clean:
	@echo "Cleaning up virtual environment and requirements.txt..."
	rm -rf .venv
	rm -f requirements.txt

# Set up the virtual environment and install dependencies
setup: clean
	@echo "Setting up Poetry environment and installing dependencies..."
	poetry install