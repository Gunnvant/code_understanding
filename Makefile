.PHONY: install dev test lint run dashboard schedule docker-up docker-down clean

install:
	pip install -e .[dev]

dev:
	pip install -e .[dev]

test:
	pytest

lint:
	ruff check etl tests

run:
	python -m etl.cli run

validate:
	python -m etl.cli validate clientes.csv

runs:
	python -m etl.cli runs

snapshots:
	python -m etl.cli snapshots

dashboard:
	python -m etl.cli dashboard

schedule:
	python -m etl.cli schedule

docker-up:
	docker compose up --build

docker-down:
	docker compose down

clean:
	rm -rf logs/*.log rejected/*.csv snapshots/*.parquet output/*.parquet etl.db
	find . -type d -name __pycache__ -exec rm -rf {} +
