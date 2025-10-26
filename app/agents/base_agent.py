# app/agents/base_agent.py
"""
Base agent interface for all static analysis agents.
TODO: Define abstract base class with run() method.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    """
    Abstract base class for all analysis agents.
    Each agent runs static analysis tools and returns standardized findings.
    """
    
    @abstractmethod
    async def run(self, repo_path: str) -> Dict[str, Any]:
        """
        Execute the agent's analysis on the given repository path.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            Standardized findings dictionary
        """
        pass
