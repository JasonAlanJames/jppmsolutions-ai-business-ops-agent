from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy.orm import Session

from app.auth import verify_google_admin_token
from app.db import get_db, init_db
from app.email_ops.approval_repository import (
    approval_to_dict,
    list_approval_decisions,
    list_email_workflow_records,
    workflow_to_dict,
)
from app.email_ops.approval_schemas import ApprovalRequest, ApprovalResult
from app.email_ops.approval_service import process_approval
from app.email_ops.gmail_triage import triage_unread_emails


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="JPPM Solutions AI Business Operations Agent",
    description=(
        "LangChain, LangGraph, Gmail API, Chroma RAG, SQLite persistence, "
        "and approval-gated AI business communications assistant for the "
        "JPPM Solutions ecosystem."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "JPPM Solutions AI Business Operations Agent",
        "version": "0.3.0",
        "safety": "No email is sent automatically. Human approval is required.",
        "auth": "Protected endpoints require Google ID token authentication.",
        "persistence": "SQLite persistence enabled for approval decisions.",
    }


@app.get("/emails/triage")
def triage_emails(
    max_results: int = 5,
    create_drafts: bool = False,
    admin: dict = Depends(verify_google_admin_token),
):
    """
    Triage unread Gmail messages through the LangGraph workflow.

    Safe defaults:
    - create_drafts=False
    - no send action exists
    - protected by Google-authenticated admin access
    """
    return {
        "admin_email": admin.get("email"),
        "results": triage_unread_emails(
            max_results=max_results,
            create_drafts=create_drafts,
        ),
    }


@app.post("/emails/approve", response_model=ApprovalResult)
def approve_email(
    request: ApprovalRequest,
    admin: dict = Depends(verify_google_admin_token),
    db: Session = Depends(get_db),
):
    """
    Approve or reject an email workflow action.

    Approval may create a Gmail draft when the workflow determines a reply is needed.
    This endpoint never sends emails automatically.
    """
    return process_approval(
        request=request,
        db=db,
    )


@app.get("/emails/approvals")
def approvals(
    admin: dict = Depends(verify_google_admin_token),
    db: Session = Depends(get_db),
):
    """
    Return persisted approval decisions for authenticated admins.
    """
    records = list_approval_decisions(db)

    return {
        "admin_email": admin.get("email"),
        "approval_log": [approval_to_dict(record) for record in records],
    }


@app.get("/emails/workflows")
def workflows(
    admin: dict = Depends(verify_google_admin_token),
    db: Session = Depends(get_db),
    limit: int = 100,
):
    """
    Return persisted email workflow records for authenticated admins.
    """
    records = list_email_workflow_records(db, limit=limit)

    return {
        "admin_email": admin.get("email"),
        "workflow_records": [workflow_to_dict(record) for record in records],
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    workflow_records = list_email_workflow_records(db, limit=25)
    approval_records = list_approval_decisions(db, limit=25)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "workflow_records": workflow_records,
            "approval_records": approval_records,
        },
)