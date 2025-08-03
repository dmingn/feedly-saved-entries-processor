.PHONY: all
all: check

.PHONY: sync
sync:
	poetry sync

.PHONY: check
check: sync
	poetry run ruff check .
	poetry run ruff format --check .
	poetry run mypy .
	poetry run pytest

.PHONY: format
format: sync
	poetry run ruff check . --fix
	poetry run ruff format .

.PHONY: format-and-check
format-and-check:
	$(MAKE) format
	$(MAKE) check
