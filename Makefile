bump:
	poetry version patch
test:
	poetry run pytest --junitxml=pytest.xml --cov-report=xml:coverage.xml --cov-report=term-missing:skip-covered --cov=pytoncenter tests/v2/** tests/v3/** tests/extension/**
# Output file
OUTPUT_FILE := ./pytoncenter/v3/models/gen-openapi.py

.PHONY: generate
generate: $(OUTPUT_FILE)
$(OUTPUT_FILE):
	poetry run datamodel-codegen --url https://toncenter.com/api/v3/openapi.json --input-file-type openapi --output $(OUTPUT_FILE)
