import os
import subprocess
import argparse
import magic

FILE_PATH = "FilePath"  # the key for the attribute, is the path for the static page and allure report zip files
CONTENT_TYPE = "ContentType"
NEOFS_WALLET_PASSWORD_ENV_NAME = "NEOFS_WALLET_PASSWORD"
PORT_8080 = 8080


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
        default=None,
    )
    parser.add_argument(
        "--url_path_prefix",
        required=False,
        type=str,
        help="This is a prefix to the url address for each of the files(objects)."
        "For example, if Container ID is HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6 and"
        "--url_path_prefix is '96-1697035975', then the url will be:"
        "  https://http.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/832-1695916423/file.txt"
        "Without --url_path_prefix the url will be:"
        "  https://http.fs.neo.org/HXSaMJXk2g8C14ht8HSi7BBaiYZ1HeWh2xnWPGQCg4H6/file.txt",
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
        default=None,
    )
    parser.add_argument(
        "--put-timeout",
        required=False,
        type=int,
        help="Timeout for the put each file to neofs, in seconds. Default is 600 seconds",
        default=600,
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


def push_file(
    directory: str,
    subdir: str,
    url_path_prefix: str,
    filename: str,
    attributes: str,
    base_cmd: str,
    put_timeout: int,
) -> None:
    filepath = os.path.join(subdir, filename)
    mime_type = magic.from_file(filepath, mime=True)
    relative_path = os.path.relpath(filepath, os.path.dirname(directory))

    if url_path_prefix is not None:
        neofs_path_attr = os.path.join(url_path_prefix, relative_path)
    else:
        neofs_path_attr = relative_path

    base_cmd_with_file = f"{base_cmd} --file {filepath} --attributes {FILE_PATH}={neofs_path_attr},{CONTENT_TYPE}={mime_type}"

    if attributes is not None:
        base_cmd_with_file += f",{attributes}"

    print(f"Neofs cli cmd is: {base_cmd_with_file}")

    try:
        compl_proc = subprocess.run(
            base_cmd_with_file,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=put_timeout,
            shell=True,
        )

        print(f"RC: {compl_proc.returncode}")
        print(f"Output: {compl_proc.stdout}")
        print(f"Error: {compl_proc.stderr}")

    except subprocess.CalledProcessError as e:
        raise Exception(
            f"Command failed: {e.cmd}\n"
            f"Error code: {e.returncode}\n"
            f"Output: {e.output}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}\n"
        )


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
) -> None:
    if not os.path.exists(directory):
        raise Exception(f"Directory '{directory}' does not exist.")
    if not os.listdir(directory):
        raise Exception(f"Directory '{directory}' is empty.")

    base_cmd = (
        f"NEOFS_CLI_PASSWORD={password} neofs-cli --rpc-endpoint {endpoint} "
        f"--wallet {wallet}  object put --cid {cid} --timeout {put_timeout}s"
    )
    if lifetime is not None and lifetime > 0:
        current_epoch = get_current_epoch(endpoint)
        expiration_epoch = current_epoch + lifetime
        base_cmd += f" --expire-at {expiration_epoch}"

    base_path = os.path.abspath(directory)
    for subdir, dirs, files in os.walk(base_path):
        for filename in files:
            push_file(
                base_path,
                subdir,
                url_path_prefix,
                filename,
                attributes,
                base_cmd,
                put_timeout,
            )


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
    )
