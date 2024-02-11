bump:
	poetry version patch
test:
	poetry run pytest --junitxml=pytest.xml --cov-report=term-missing:skip-covered --cov=pytoncenter tests/**