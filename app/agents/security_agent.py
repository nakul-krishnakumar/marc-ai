# app/agents/security_agent.py
"""
Security agent for running Bandit and Semgrep static analysis.
TODO: Implement subprocess calls to Bandit/Semgrep with proper safety measures.
"""
from typing import Any

from app.agents.base_agent import BaseAgent


class SecurityAgent(BaseAgent):
    """
    Runs security checks using Bandit and Semgrep.
    """

    async def run(self, repo_path: str) -> dict[str, Any]:
        # TODO: Implement safe subprocess calls
        return {"agent": "security", "findings": []}
