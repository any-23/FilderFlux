.PHONY: flake8 black mypy lint test

flake8:
	flake8 . --toml-config=pyproject.toml

black:
	black .

mypy:
	mypy .

lint: flake8 black mypy

test:
	pytest
