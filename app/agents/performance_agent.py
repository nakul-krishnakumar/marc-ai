# app/agents/performance_agent.py
"""
Performance agent for running Radon complexity analysis.
TODO: Implement subprocess calls to Radon with proper safety measures.
"""
from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class PerformanceAgent(BaseAgent):
    """
    Runs complexity and performance analysis using Radon.
    """
    
    async def run(self, repo_path: str) -> Dict[str, Any]:
        # TODO: Implement safe subprocess calls
        return {"agent": "performance", "findings": []}
