import os
import re
import subprocess
import argparse
import magic
import mimetypes
from helpers.neofs import neofs_cli_execute

FILE_PATH = "FilePath"  # the key for the attribute, is the path for the static page and allure report zip files
CONTENT_TYPE = "Content-Type"
NEOFS_WALLET_PASSWORD_ENV_NAME = "NEOFS_WALLET_PASSWORD"
PORT_8080 = 8080


def str_to_bool(value):
    """Convert a string representation of a boolean value to a boolean."""
    value_lower = value.strip().lower()
    if value_lower in {'true', 't', 'yes', 'y', '1'}:
        return True
    elif value_lower in {'false', 'f', 'no', 'n', '0'}:
        return False
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def parse_args():
    parser = argparse.ArgumentParser(description="Process allure reports")
    parser.add_argument(
        "--neofs_domain",
        required=True,
        type=str,
        help="NeoFS network domain, example: st1.storage.fs.neo.org",
    )
    parser.add_argument("--wallet", required=True, type=str, help="Path to the wallet")
    parser.add_argument("--cid", required=True, type=str, help="Container ID")
    parser.add_argument(
        "--attributes",
        required=False,
        type=str,
        help="User attributes in form of Key1=Value1,Key2=Value2"
        "For example, it's convenient to create url links to access an object via http:"
        "FilePath=96-1697035975/dir/3.txt"
        "Type=test_result,Master=true,RUN_ID=96-1697035975",
        nargs="?",
        const=None,
        default=None,
    )
    parser.add_argument(
        "--url_path_prefix",
        required=False,
        type=str,
        help="This is a prefix to the url address for each of the files(objects)."
        "For example, if Container ID is HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6 and"
        "--url_path_prefix is '96-1697035975', then the url will be:"
        "  https://rest.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/832-1695916423/file.txt"
        "Without --url_path_prefix the url will be:"
        "  https://rest.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/file.txt",
        nargs="?",
        const=None,
        default=None,
    )
    parser.add_argument(
        "--files-dir",
        required=True,
        type=str,
        help="Path to the directory with the files to be pushed",
    )
    parser.add_argument(
        "--lifetime",
        required=False,
        type=int,
        help="Lifetime in epochs - number of epochs for object to stay valid. If provided, will be added to the "
        "current epoch to calculate expiration epoch. If not provided, or if it is 0, the report will be stored "
        "indefinitely",
        nargs="?",
        const=None,
        default=None,
    )
    parser.add_argument(
        "--put-timeout",
        required=False,
        type=int,
        help="Timeout for the put each file to neofs, in seconds. Default is 600 seconds",
        default=600,
    )
    parser.add_argument(
        "--strip-prefix",
        required=False,
        type=str_to_bool,
        help="Treat files-dir as the root of container (removing it from FilePath)",
        default=False,
    )
    parser.add_argument(
        "--replace-objects",
        required=False,
        type=str_to_bool,
        help="Replace existing objects with the same attributes in the container",
        default=True,
    )
    parser.add_argument(
        "--replace-container-contents",
        required=False,
        type=str_to_bool,
        help="Remove all the old existing objects in the container after the new objects are uploaded",
        default=False,
    )

    return parser.parse_args()


def get_password() -> str:
    password = os.getenv(NEOFS_WALLET_PASSWORD_ENV_NAME)
    return password


def get_current_epoch(endpoint: str) -> int:
    cmd = f"neofs-cli netmap epoch --rpc-endpoint {endpoint}"
    epoch_str = subprocess.check_output(cmd, shell=True).strip().decode("utf-8")
    return int(epoch_str)


def get_rpc_endpoint(neofs_domain: str) -> str:
    return f"{neofs_domain}:{PORT_8080}"


def search_objects_in_container(endpoint: str,
                                wallet: str,
                                password: str,
                                cid: str,
                                filters: str) -> list[str]:
    cmd = (
        f"NEOFS_CLI_PASSWORD={password} neofs-cli --rpc-endpoint {endpoint} "
        f"--wallet {wallet} object search --cid {cid} --filters '{filters}'"
    )
    output_filter_re = re.compile(r"^Found \d+ objects\.$")
    stdout_list = neofs_cli_execute(cmd)
    filtered_lines = [line for line in stdout_list if not output_filter_re.search(line)]
    return filtered_lines


def list_objects_in_container(endpoint: str,
                              wallet: str,
                              password: str,
                              cid: str) -> list[str]:
    cmd = (
        f"NEOFS_CLI_PASSWORD={password} neofs-cli --rpc-endpoint {endpoint} "
        f"--wallet {wallet} container list-objects --cid {cid}"
    )
    return neofs_cli_execute(cmd)


def delete_objects(
    endpoint: str,
    wallet: str,
    password: str,
    cid: str,
    oids: list[str],
) -> None:
    for oid in oids:
        cmd = (
            f"NEOFS_CLI_PASSWORD={password} neofs-cli --rpc-endpoint {endpoint} "
            f"--wallet {wallet} object delete --cid {cid} --oid '{oid}'"
        )
        try:
            neofs_cli_execute(cmd)
        except Exception as e:
            if "object already removed" not in str(e):
                raise e


def compile_attributes(file_path: str, content_type: str = None,
                       attributes: str = None, output_format: str = "str") -> str:
    attrs = {
        FILE_PATH: file_path,
    }
    if content_type:
        attrs[CONTENT_TYPE] = content_type
    if attributes:
        attrs.update(dict([attr.split('=') for attr in attributes.split(',')]))
    if output_format == "str":
        return ','.join([f"{k}={v}" for k, v in attrs.items()])
    elif output_format == "filter_str":
        return ','.join([f"{k} EQ {v}" for k, v in attrs.items()])
    elif output_format == "dict":
        return attrs


def get_file_info(directory: str, url_path_prefix: str, strip_prefix: bool):
    base_path = os.path.abspath(directory)
    relative_base = directory
    if not strip_prefix:
        relative_base = os.path.dirname(directory)
    file_infos = []

    for subdir, dirs, files in os.walk(base_path):
        for filename in files:
            filepath = os.path.join(subdir, filename)
            mime_type = mimetypes.guess_type(filepath)[0]
            if not mime_type:
                mime_type = magic.from_file(filepath, mime=True)
            relative_path = os.path.relpath(filepath, relative_base)

            if url_path_prefix is not None and url_path_prefix != "":
                neofs_path_attr = os.path.join(url_path_prefix, relative_path)
            else:
                neofs_path_attr = relative_path

            file_infos.append({
                'filepath': filepath,
                'mime_type': mime_type,
                'neofs_path_attr': neofs_path_attr,
            })

    return file_infos


def push_file(
    endpoint: str,
    wallet: str,
    password: str,
    cid: str,
    file_info: dict,
    attributes: str,
    put_timeout: int,
    expiration_epoch: int = None,
) -> None:
    filepath = file_info['filepath']
    mime_type = file_info['mime_type']
    neofs_path_attr = file_info['neofs_path_attr']

    attrs = compile_attributes(neofs_path_attr, mime_type, attributes)

    base_cmd = (
        f"NEOFS_CLI_PASSWORD={password} neofs-cli --rpc-endpoint {endpoint} "
        f"--wallet {wallet}  object put --cid {cid} --timeout {put_timeout}s --no-progress"
    )
    if expiration_epoch:
        base_cmd += f" --expire-at {expiration_epoch}"

    cmd = f"{base_cmd} --file {filepath} --attributes {attrs}"
    print(f"Neofs cli cmd is: {cmd}")

    neofs_cli_execute(cmd, timeout=put_timeout)


def push_files_to_neofs(
    directory: str,
    endpoint: str,
    wallet: str,
    cid: str,
    attributes: str,
    url_path_prefix: str,
    lifetime: int,
    put_timeout: int,
    password: str,
    strip_prefix: bool,
    replace_objects: bool,
    replace_container_contents: bool
) -> None:
    if not os.path.exists(directory):
        raise Exception(f"Directory '{directory}' does not exist.")
    if not os.listdir(directory):
        raise Exception(f"Directory '{directory}' is empty.")

    expiration_epoch = None
    if lifetime is not None and lifetime > 0:
        current_epoch = get_current_epoch(endpoint)
        expiration_epoch = current_epoch + lifetime

    files = get_file_info(directory, url_path_prefix, strip_prefix)
    flat_existing_objects = []
    if replace_container_contents:
        flat_existing_objects = list_objects_in_container(endpoint, wallet, password, cid)
    elif replace_objects:
        existing_objects = []
        for file in files:
            search_attrs = compile_attributes(
                file['neofs_path_attr'], output_format="filter_str"
            )
            obj_to_delete = search_objects_in_container(
                endpoint, wallet, password, cid, search_attrs
            )
            existing_objects.append(obj_to_delete)
        flat_existing_objects = [obj for sublist in existing_objects for obj in
                                 (sublist if isinstance(sublist, list) else [sublist])]

    for file in files:
        push_file(
            endpoint,
            wallet,
            password,
            cid,
            file,
            attributes,
            put_timeout,
            expiration_epoch,
        )

    if flat_existing_objects:
        delete_objects(endpoint, wallet, password, cid, flat_existing_objects)


if __name__ == "__main__":
    args = parse_args()
    neofs_password = get_password()
    rpc_endpoint = get_rpc_endpoint(args.neofs_domain)

    push_files_to_neofs(
        args.files_dir,
        rpc_endpoint,
        args.wallet,
        args.cid,
        args.attributes,
        args.url_path_prefix,
        args.lifetime,
        args.put_timeout,
        neofs_password,
        args.strip_prefix,
        args.replace_objects,
        args.replace_container_contents,
    )
