import logging
import subprocess

logger = logging.getLogger(__name__)

KUBECTL_NAME = "kubectl"

PROCESS_TIMEOUT=10

def run_kubectl(command_args: list[str], *, stdin: str = None) -> str:
    try:
        command_args = command_args or []
        command_args = [x.strip() for x in command_args]
        if ("-w" in command_args) or ("--watch" in command_args):
            return "Unable to run kubectl with the --watch or -w flags, please modify your call to exclude this parameter"
        command_items = [KUBECTL_NAME, *command_args]
        result = subprocess.run(args=command_items, input=stdin, text=True, check=True, capture_output=True,timeout=PROCESS_TIMEOUT)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.exception(
            f"Failed to run kubectl with args: {command_args}\n"
            f"stdin: {stdin}\n"
            f"exit code: {e.returncode}\n"
            f"stderr: {e.stderr}\n"
            f"stdout: {e.stdout}"
        )
        raise Exception(f"kubectl exited with code {e.returncode}: {e.stderr}")
    except:
        logger.exception(f"Failed to run kubectl, params: {command_args}")
        raise
