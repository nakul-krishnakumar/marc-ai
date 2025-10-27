import operator
from typing import Annotated, TypedDict

from app.agents.auditor_agent import Files
from app.agents.security_agent import SecurityFindings


class RepoAnalysisState(TypedDict):
    log_all_audits: bool
    repo_path: str
    files: Files
    style_findings: Annotated[list[dict], operator.add]
    security_findings: SecurityFindings
    performance_findings: Annotated[list[dict], operator.concat]
    merged_findings: list[dict] | None
    markdown_report: str | None
