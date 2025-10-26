import operator
from typing import Annotated, TypedDict

from app.agents.auditor_agent import Files


class RepoAnalysisState(TypedDict):
    repo_path: str
    files: Files
    style_findings: Annotated[list[dict], operator.add]
    security_findings: Annotated[list[dict], operator.add]
    performance_findings: Annotated[list[dict], operator.add]
    merged_findings: list[dict] | None
    markdown_report: str | None
