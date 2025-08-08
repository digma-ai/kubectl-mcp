import asyncio
import contextlib
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

KUBECTL_NAME = "kubectl"

PROCESS_TIMEOUT = 10


class PassThroughError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


async def run_kubectl(command_args: list[str], *, stdin: str = None) -> str:
    try:
        args = [x.strip() for x in (command_args or [])]
        if ("-w" in args) or ("--watch" in args):
            return (
                "Unable to run kubectl with the --watch or -w flags, please modify your call to exclude this parameter"
            )

        proc = await asyncio.create_subprocess_exec(
            KUBECTL_NAME,
            *args,
            stdin=asyncio.subprocess.PIPE if stdin is not None else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        logger.debug('[Kubectl PID %s] Process started "%s"', proc.pid, _ellipsis(" ".join([KUBECTL_NAME, *args]), 50))

        try:
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(input=stdin.encode() if stdin is not None else None),
                timeout=PROCESS_TIMEOUT,
            )
            logger.debug("[Kubectl PID %s] Process finished", proc.pid)
            stdout = stdout_b.decode()
            stderr = stderr_b.decode()
            if proc.returncode != 0:
                logger.exception(
                    f"Failed to run kubectl with args: {command_args}\n"
                    f"stdin: {stdin}\n"
                    f"exit code: {proc.returncode}\n"
                    f"stderr: {stderr}\n"
                    f"stdout: {stdout}"
                )
                raise PassThroughError(f"kubectl exited with code {proc.returncode}: {stderr}")

            return stdout

        except asyncio.TimeoutError:
            logger.exception("kubectl timed out after %s seconds; args=%s; stdin=%s", PROCESS_TIMEOUT, args, stdin)
            logger.debug("[Kubectl PID %s] Sending SIGKILL to process", proc.pid)
            with contextlib.suppress(ProcessLookupError):
                proc.kill()
            logger.debug("[Kubectl PID %s] Waiting to finish", proc.pid)
            await proc.wait()
            logger.debug("[Kubectl PID %s] Process finished", proc.pid)
            raise PassThroughError(f"kubectl timed out after {PROCESS_TIMEOUT} seconds")

    except PassThroughError:
        raise

    except:
        logger.exception(f"Failed to run kubectl, params: {command_args}")
        raise


def _ellipsis(text, max_length):
    if not text or len(text) <= max_length:
        return text
    trimmed = text[: max_length - 3].rsplit(" ", 1)[0]
    return trimmed + "..."
