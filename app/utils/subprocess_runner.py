import subprocess
from pathlib import Path
from typing import Any


def run_safe_subprocess(
    command: list[str],
    cwd: str | Path | None = None,
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
    try:
        result = subprocess.run(
            command,
            check=False,
            env=env,
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            shell=False,
        )

        print(f"Command: {' '.join(command)}")
        print(f"Return code: {result.returncode}")

        output: dict[str, Any] = {
            "stdout": result.stdout.decode('utf-8', errors='ignore'),
            "stderr": result.stderr.decode('utf-8', errors='ignore'),
            "returncode": result.returncode,
        }

        return output
    
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout}s: {' '.join(command)}")
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "returncode": -1,
        }
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }
