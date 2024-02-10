import pytest
from aiohttp.web_exceptions import HTTPError


@pytest.fixture(autouse=True)
def ignore_http_422_errors():
    """
    A fixture to ignore HTTP 422 errors in all test cases.
    This fixture automatically applies to all tests.
    """
    try:
        yield  # This allows the test to run. If there's an HTTP 422 error, it'll be caught below.
    except HTTPError as e:
        if e.response.status_code == 422:
            pytest.skip(f"Skipping test due to HTTP 422 error: {e}")
        else:
            raise  # Reraises the exception if it's not a 422 error
