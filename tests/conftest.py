import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--base_url", action="store", default=None, help="Base URL to test against"
    )
    parser.addoption(
        "--report_dir",
        action="store",
        default=None,
        help="Directory combine report and zip files",
    )


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base_url")


@pytest.fixture
def report_dir(request):
    return request.config.getoption("--report_dir")
