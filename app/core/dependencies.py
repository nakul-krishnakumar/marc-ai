# # app/core/dependencies.py
# # from langchain_openai import AzureChatOpenAI
# from app.core.config import settings

def get_orchestrator():
    """
    Return an orchestrator / LangGraph client instance.
    This is a factory placeholder — do not initialize heavy clients at import time.
    """
    class AnalysisOrchestrator:
        def __init__(self):
            pass
            # self.llm = AzureChatOpenAI(
            #     model="gpt-4o",
            #     temperature=0,
            #     azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            #     api_key=settings.AZURE_OPENAI_API_KEY,
            #     api_version=settings.AZURE_OPENAI_API_VERSION,
            #     azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
            # )

        # def run(self, input_data):
        #     # return self.llm.invoke(input_data)

    return AnalysisOrchestrator()

