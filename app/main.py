from fastapi import Depends, FastAPI

from app.auth import verify_google_admin_token
from app.email_ops.approval_schemas import ApprovalRequest, ApprovalResult
from app.email_ops.approval_service import get_approval_log, process_approval
from app.email_ops.gmail_triage import triage_unread_emails


app = FastAPI(
    title="JPPM Solutions AI Business Operations Agent",
    description=(
        "LangChain, LangGraph, Gmail API, Chroma RAG, and approval-gated "
        "AI business communications assistant for the JPPM Solutions ecosystem."
    ),
    version="0.2.0",
)


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "JPPM Solutions AI Business Operations Agent",
        "version": "0.2.0",
        "safety": "No email is sent automatically. Human approval is required.",
        "auth": "Protected endpoints require Google ID token authentication.",
    }


@app.get("/emails/triage")
def triage_emails(
    max_results: int = 5,
    create_drafts: bool = False,
    admin: dict = Depends(verify_google_admin_token),
):
    """
    Triage unread Gmail messages through the LangGraph workflow.

    Safe default:
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
):
    """
    Record human approval or rejection.

    Approval can create a Gmail draft when the workflow determines a reply is needed.
    This endpoint never sends emails automatically.
    """
    return process_approval(request)


@app.get("/emails/approvals")
def approvals(
    admin: dict = Depends(verify_google_admin_token),
):
    """
    Return approval log for authenticated admins.
    """
    return {
        "admin_email": admin.get("email"),
        "approval_log": get_approval_log(),
    }