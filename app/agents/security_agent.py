from typing import Any



class SecurityAgent:
    """
    Runs security checks using Bandit and Semgrep.
    """

    async def run(self, repo_path: str) -> dict[str, Any]:
        # TODO: Implement safe subprocess calls
        return {"agent": "security", "findings": []}
