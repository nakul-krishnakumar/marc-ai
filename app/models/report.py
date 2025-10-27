# app/models/report.py
from typing import Any

from pydantic import BaseModel, ConfigDict


class AgentFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent: str
    findings: list[dict[str, Any]]
    metadata: dict[str, Any] | None = None


class ConsolidatedReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str
    repo_url: str
    summary: str | None = None
    findings: list[AgentFinding] = []
    markdown: str | None = None
