import operator
from typing import Annotated, TypedDict, Any

from app.agents.auditor_agent import Files
from app.agents.performance_agent import PerformanceFindings
from app.agents.security_agent import SecurityFindings
from langchain_openai import AzureChatOpenAI



class RepoAnalysisState(TypedDict):
    llm: AzureChatOpenAI
    log_all_audits: bool
    repo_path: str
    files: Files
    style_findings: Annotated[list[dict], operator.add]
    security_findings: SecurityFindings
    performance_findings: PerformanceFindings
    merged_findings: list[dict[str, Any]] | None
    markdown_report: str | None
