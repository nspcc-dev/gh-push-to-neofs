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
    parser.addoption(
        "--data_dir_prefix",
        action="store",
        default=None,
        help="Prefix dir to add to modified test data",
    )


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base_url")


@pytest.fixture
def report_dir(request):
    return request.config.getoption("--report_dir")


@pytest.fixture
def data_dir_prefix(request):
    return request.config.getoption("--data_dir_prefix")
