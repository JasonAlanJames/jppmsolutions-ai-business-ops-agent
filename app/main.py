from fastapi import FastAPI

from app.email_ops.approval_schemas import ApprovalRequest, ApprovalResult
from app.email_ops.approval_service import get_approval_log, process_approval
from app.email_ops.gmail_triage import triage_unread_emails

app = FastAPI(
    title="JPPM Solutions AI Business Operations Agent",
    description=(
        "LangChain, LangGraph, Gmail API, and RAG-powered business operations agent "
        "with human-in-the-loop approval."
    ),
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "JPPM Solutions AI Business Operations Agent",
        "safety": "No email is sent automatically. Human approval is required.",
    }


@app.get("/emails/triage")
def triage_emails(max_results: int = 5, create_drafts: bool = False):
    """
    Triage unread Gmail messages through the LangGraph workflow.

    Safe default:
    - create_drafts=False
    - no send action exists
    """
    return triage_unread_emails(
        max_results=max_results,
        create_drafts=create_drafts,
    )


@app.post("/emails/approve", response_model=ApprovalResult)
def approve_email(request: ApprovalRequest):
    """
    Record human approval or rejection.

    This endpoint does not send emails.
    It only records the review decision.
    """
    return process_approval(request)


@app.get("/emails/approvals")
def approvals():
    return {
        "approval_log": get_approval_log(),
    }