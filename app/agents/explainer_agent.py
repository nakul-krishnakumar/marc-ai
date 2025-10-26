# app/agents/explainer_agent.py
"""
Explainer agent using Azure OpenAI for generating contextualized explanations.
TODO: Implement Azure OpenAI integration for report generation.
"""
from typing import Any


class ExplainerAgent:
    """
    Generates human-readable explanations and markdown reports using Azure OpenAI.
    """

    async def explain(self, findings: list[dict[str, Any]]) -> str:
        # TODO: Implement Azure OpenAI API calls
        return "# Analysis Report\n\nTODO: Generate markdown report"
