# app/routers/code_review.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.core.dependencies import get_orchestrator
from app.models.report import ConsolidatedReport
from app.models.requests import RepoRequest

router = APIRouter()

@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_repo(
    payload: RepoRequest,
    background_tasks: BackgroundTasks,
    orchestrator=Depends(get_orchestrator)):
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
