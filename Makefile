.PHONY: setup data db load analyze pipeline dashboard test check
BIN := .venv/bin
setup:
	python3 -m venv .venv
	$(BIN)/python -m pip install -e '.[dev]'
data:
	$(BIN)/igaming generate
	$(BIN)/igaming clean
db:
	docker compose up -d --wait
load:
	$(BIN)/igaming load
analyze:
	$(BIN)/igaming analyze
pipeline: db
	$(BIN)/igaming all
dashboard:
	$(BIN)/streamlit run app.py
test:
	$(BIN)/pytest -m 'not integration'
check:
	$(BIN)/ruff check src tests app.py
	$(BIN)/ruff format --check src tests app.py
	$(BIN)/pytest
