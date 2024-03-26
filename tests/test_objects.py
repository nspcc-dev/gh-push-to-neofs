import sys
import json
import pytest
from conftest import DATA_PATH_LIST

sys.path.insert(0, '..')
from helpers.neofs import neofs_cli_execute


def test_objects_number(wallet, wallet_password, network_domain, cid):
    cmd = (
        f"NEOFS_CLI_PASSWORD={wallet_password} neofs-cli --rpc-endpoint {network_domain}:8080 "
        f"--wallet {wallet} container list-objects --cid {cid}"
    )
    objects_json = neofs_cli_execute(cmd, json_output=True)
    objects_list = json.loads(objects_json)
    obj_number = len(objects_list)
    files_num = len(DATA_PATH_LIST)
    assert (
        obj_number == files_num
    ), f"Objects number of {obj_number} in the container and the number {files_num} of uploaded files doesn't match"
