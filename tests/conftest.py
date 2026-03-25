import os
import pytest


DATA_PATH_LIST = [
        "1.txt",
        "2.txt",
        "dir/3.txt",
        "dir/subdir/4.txt",
        "dir/subdir/subdir_2/5.txt",
    ]


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
    parser.addoption("--wallet", action="store", help="NeoFS wallet")
    parser.addoption("--wallet-password", action="store", help="NeoFS wallet password")
    parser.addoption("--neofs-endpoint", action="store", help="NeoFS RPC endpoint")
    parser.addoption("--cid", action="store", help="NeoFS Container ID")


@pytest.fixture
def base_url(request):
    return os.environ.get('BASE_URL') or request.config.getoption("--base_url")


@pytest.fixture
def report_dir(request):
    return os.environ.get('REPORT_DIR') or request.config.getoption("--report_dir")


@pytest.fixture
def data_dir_prefix(request):
    return os.environ.get('DATA_DIR_PREFIX') or request.config.getoption("--data_dir_prefix")


@pytest.fixture
def wallet(request):
    return os.environ.get('NEOFS_WALLET') or request.config.getoption("--wallet")


@pytest.fixture
def wallet_password(request):
    return os.environ.get('NEOFS_WALLET_PASSWORD') or request.config.getoption("--wallet-password")


@pytest.fixture
def neofs_endpoint(request):
    return os.environ.get('NEOFS_ENDPOINT') or request.config.getoption("--neofs-endpoint")


@pytest.fixture
def cid(request):
    return os.environ.get('STORE_OBJECTS_CID') or request.config.getoption("--cid")
