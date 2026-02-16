PYTHON ?= python3

.PHONY: install pipeline dbt-run dbt-test train-model dashboard schedule test

install:
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e ".[dev]"

pipeline:
	$(PYTHON) scripts/run_pipeline.py

dbt-run:
	dbt run --project-dir dbt --profiles-dir dbt

dbt-test:
	dbt test --project-dir dbt --profiles-dir dbt

train-model:
	$(PYTHON) scripts/train_model.py

dashboard:
	streamlit run dashboard/app.py

schedule:
	$(PYTHON) scripts/run_scheduler.py

test:
	pytest
