# app/agents/performance_agent.py
"""
Performance agent for running Radon complexity analysis.
TODO: Implement subprocess calls to Radon with proper safety measures.
"""
from typing import Any

from app.agents.base_agent import BaseAgent


class PerformanceAgent(BaseAgent):
    """
    Runs complexity and performance analysis using Radon.
    """

    async def run(self, repo_path: str) -> dict[str, Any]:
        # TODO: Implement safe subprocess calls
        return {"agent": "performance", "findings": []}
