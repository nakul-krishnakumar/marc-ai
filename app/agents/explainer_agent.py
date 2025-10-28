

from typing import Any
from langchain_openai import AzureChatOpenAI

from app.core.logger import logger

class ExplainerAgent:
    """
    Generates human-readable explanations and markdown reports using Azure OpenAI.
    """

    def __init__(self, findings: list[dict[str, Any]] | None, llm: AzureChatOpenAI):
        self.findings = findings
        self.llm = llm

    def run(self) -> str:
        
        logger.info("Explainer Agent: generating explanation report...")
        output = self.llm.invoke("Explain the following findings in detail:\n" + str(self.findings))
        logger.info("Generated explanation using LLM.")
        logger.debug(f"Findings explanation: {output}")

        with open("explanation_report.md", "w") as f:
            f.write(str(output.content))

        return "# Analysis Report\n\nTODO: Generate markdown report"
