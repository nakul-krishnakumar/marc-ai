from typing import Any

from app.agents.base_agent import BaseAgent
from app.utils.subprocess_runner import run_safe_subprocess


class StyleAgent(BaseAgent):
    """
    Runs style and formatting checks using Ruff (Python) and ESLint (JS).
    """

    def run(self, repo_path: str) -> dict[str, Any]:
        """Run style checks on the repository."""
        findings = []
        
        # Run Ruff for Python
        cmd = ["ruff", "check", repo_path, "--output-format=json"]
        ruff_result = run_safe_subprocess(cmd, cwd=repo_path)
        
        if ruff_result["stdout"]:
            findings.append({
                "tool": "ruff",
                "output": ruff_result["stdout"],
                "errors": ruff_result["stderr"]
            })
        
        # TODO: Run ESLint for JavaScript
        # eslint_result = run_safe_subprocess(["eslint", repo_path, "--format=json"])
        
        # print("StyleAgent findings:", findings)   
        return {"agent": "style", "findings": findings}
