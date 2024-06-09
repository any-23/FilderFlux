.PHONY: flake8 black mypy lint pytest

flake8:
	flake8 . --toml-config=pyproject.toml

black:
	black .

mypy:
	mypy .

lint: flake8 black mypy

test:
	pytest
