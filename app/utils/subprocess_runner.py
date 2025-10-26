import subprocess
from pathlib import Path
from typing import Any


def run_safe_subprocess(
    command: list[str],
    cwd: Path | None = None,
    timeout: int = 300,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Execute a subprocess safely with proper isolation and timeouts.

    Args:
        command: Command as list (never use shell=True)
        cwd: Working directory
        timeout: Timeout in seconds
        env: Environment variables

    Returns:
        Dict with stdout, stderr, returncode
    """

    result = subprocess.run(
        command,
        check=True,
        env=env,
        cwd=cwd,
        capture_output=True,
        timeout=timeout,
        shell=False,
    )

    output: dict[str, Any] = {
        "stdout": result.stdout.decode(),
        "stderr": result.stderr.decode(),
        "returncode": result.returncode,
    }

    return output
