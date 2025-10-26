# app/routers/code_review.py
import subprocess
import tempfile

import requests
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.core.dependencies import get_orchestrator
from app.models.report import ConsolidatedReport
from app.models.requests import RepoRequest
from app.services.code_review_service import CodeReviewService

router = APIRouter()

@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_repo(
    payload: RepoRequest,
    background_tasks: BackgroundTasks,
    orchestrator=Depends(get_orchestrator)
):
    try:
        repo_url = str(payload.repo_url)
        ref = str(payload.ref)
        scan_id = str(payload.scan_id)

        code_reviewer = CodeReviewService(repo_url, ref, scan_id)
        code_reviewer.clone_repo()

        """
        Trigger analysis run. This endpoint enqueues a workflow and returns a run_id.
        Business logic should:
        - validate and clone repo into a temp workspace
        - schedule agents (via LangGraph orchestrator)
        - persist run metadata
        """
        run_id = "run_stub_id"  # TODO: replace with generated id
        # TODO: enqueue background workflow using orchestrator
        return {"run_id": run_id, "message": "Analysis scheduled."}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/status/{run_id}")
async def get_status(run_id: str):
    """
    Returns the current state of a run (queued/ running / completed / failed).
    """
    return {"run_id": run_id, "status": "queued"}

@router.get("/report/{run_id}", response_model=ConsolidatedReport)
async def get_report(run_id: str):
    """
    Return consolidated report (JSON + markdown). If still running, return 202.
    """
    # TODO: lookup persisted report
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
