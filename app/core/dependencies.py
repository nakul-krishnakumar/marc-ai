from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr

from app.core.config import settings
from app.workflows.code_review_workflow import build_workflow


def get_orchestrator():
    """
    Return an orchestrator / LangGraph client instance.
    This is a factory placeholder — do not initialize heavy clients at import time.
    """

    class AnalysisOrchestrator:
        def __init__(self):
            self.llm = AzureChatOpenAI(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                temperature=0.3,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                api_key=SecretStr(settings.AZURE_OPENAI_API_KEY),
            )

            self.graph = build_workflow()
            self.state = {}

            # Debug: print the workflow graph
            print(self.graph.get_graph().draw_ascii())

        def run(self, tmpdir: str) -> None:
            self.state["repo_path"] = tmpdir
            self.graph.invoke(self.state)
            return

    return AnalysisOrchestrator()
