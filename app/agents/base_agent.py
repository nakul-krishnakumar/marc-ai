from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Abstract base class for all analysis agents.
    Each agent runs static analysis tools and returns standardized findings.
    """

    @abstractmethod
    async def run(self, repo_path: str) -> dict[str, Any]:
        """
        Execute the agent's analysis on the given repository path.

        Args:
            repo_path: Path to the cloned repository

        Returns:
            Standardized findings dictionary
        """
        pass
