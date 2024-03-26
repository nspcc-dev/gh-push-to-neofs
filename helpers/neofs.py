import subprocess
import json


def neofs_cli_execute(cmd: str, json_output: bool = False, timeout: int = None):
    """
    Executes a given command and returns its output.

    :param cmd: Command to execute.
    :param json_output: Specifies if the command output is JSON.
    :param timeout: Optional timeout for command execution.
    :return: Command output as a string or a JSON object.
    """

    try:
        compl_proc = subprocess.run(
            cmd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            shell=True,
        )

        print(f"RC: {compl_proc.returncode}")
        print(f"Output: {compl_proc.stdout}")

        if json_output:
            try:
                return json.loads(compl_proc.stdout)
            except json.JSONDecodeError:
                output_list = compl_proc.stdout.splitlines()
                return json.dumps(output_list)
        else:
            return compl_proc.stdout.splitlines()

    except subprocess.CalledProcessError as e:
        raise Exception(
            f"Command failed: {e.cmd}\n"
            f"Error code: {e.returncode}\n"
            f"Output: {e.output}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}\n"
        )
