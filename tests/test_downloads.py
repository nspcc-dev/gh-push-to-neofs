import os
import requests
import pytest
from urllib.parse import urljoin


def download_file(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


@pytest.mark.parametrize(
    "path",
    [
        "data/1.txt",
        "data/2.txt",
        "data/dir/3.txt",
        "data/dir/subdir/4.txt",
        "data/dir/subdir/subdir_2/5.txt",
    ],
)
def test_file_content(base_url, report_dir, path):
    if base_url is None:
        pytest.fail("base_url is not provided. Provide it using --base_url option.")

    if not base_url.endswith("/"):
        base_url += "/"
    full_url = base_url
    if report_dir is not None:
        full_url = urljoin(base_url, report_dir)
        if not full_url.endswith("/"):
            full_url += "/"
    full_url = urljoin(full_url, path)
    print(f"full_url: {full_url}")

    remote_content = download_file(full_url)
    with open(path, "r") as local_file:
        local_content = local_file.read()

    assert (
        remote_content == local_content
    ), f"Contents of {full_url} and {path} do not match."
