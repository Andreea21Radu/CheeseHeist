PYTHON := python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

.PHONY: help setup install run test clean format check

help:
	@echo "Available commands:"
	@echo "  make setup    - create the virtual environment and install dependencies"
	@echo "  make install  - install dependencies"
	@echo "  make run      - start the game"
	@echo "  make test     - run all tests"
	@echo "  make check    - check that the project imports correctly"
	@echo "  make clean    - remove Python cache files"

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

install:
	$(VENV_PIP) install -r requirements.txt

run:
	$(VENV_PYTHON) main.py

test:
	$(VENV_PYTHON) -m pytest tests -v

check:
	$(VENV_PYTHON) -m compileall \
		main.py \
		config \
		core \
		entities \
		generation \
		graphics \
		difficulty \
		learning

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete