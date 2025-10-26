# app/models/report.py
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any

class AgentFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent: str
    findings: List[Dict[str, Any]]
    metadata: Dict[str, Any] | None = None

class ConsolidatedReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str
    repo_url: str
    summary: str | None = None
    findings: List[AgentFinding] = []
    markdown: str | None = None
