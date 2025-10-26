import operator
from typing import Annotated, TypedDict


class RepoAnalysisState(TypedDict):
    repo_path: str
    python_files: list[str]
    js_files: list[str]
    style_findings: Annotated[list[dict], operator.add]
    security_findings: Annotated[list[dict], operator.add]
    performance_findings: Annotated[list[dict], operator.add]
    merged_findings: list[dict] | None
    markdown_report: str | None
