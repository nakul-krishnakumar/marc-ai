# app/models/requests.py
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class RepoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    repo_url: HttpUrl = Field(..., description="Git URL to repository")
    ref: str | None = Field(None, description="branch, tag, or commit")
    scan_id: str | None = Field(None, description="optional client-provided id")
