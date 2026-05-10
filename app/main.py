from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
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
    search_email_workflow_records,
    workflow_to_dict,
)
from app.email_ops.approval_schemas import ApprovalRequest, ApprovalResult
from app.email_ops.approval_service import process_approval
from app.email_ops.gmail_triage import triage_unread_emails
from app.email_ops.gmail_search import search_gmail_messages

import os

from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

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

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "dev-only-change-me"),
)

oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET") or os.getenv("GMAIL_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
    },
)

@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")


@app.get("/health")
def health():
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


def redirect_to_dashboard(message: str):
    return RedirectResponse(
        url=f"/dashboard?message={message}",
        status_code=303,
    )


def require_dashboard_user(request: Request) -> dict:
    user = request.session.get("user")

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Dashboard login required.",
        )

    return user

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    admin: dict = Depends(require_dashboard_user),
    db: Session = Depends(get_db),
    message: str | None = None,
    q: str | None = None,
    live_gmail: bool = False,
):
    if q and q.strip():
        workflow_records = search_email_workflow_records(
            db,
            query=q,
            limit=50,
        )
    else:
        workflow_records = list_email_workflow_records(
            db,
            limit=25,
        )

    approval_records = list_approval_decisions(
        db,
        limit=25,
    )

    gmail_results = []

    if live_gmail and q and q.strip():
        gmail_results = search_gmail_messages(
            query=q,
            max_results=10,
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "workflow_records": workflow_records,
            "approval_records": approval_records,
            "admin_email": admin.get("email"),
            "message": message,
            "q": q or "",
            "live_gmail": live_gmail,
            "gmail_results": gmail_results,
        },
    )


@app.post("/dashboard/triage")
def dashboard_run_triage(
    request: Request,
    admin: dict = Depends(require_dashboard_user),
    db: Session = Depends(get_db),
):
    triage_unread_emails(
        max_results=5,
        create_drafts=False,
        db=db,
    )

    return RedirectResponse(
        url="/dashboard",
        status_code=303,
    )


@app.post("/dashboard/approve/{message_id}")
def dashboard_approve_email(
    message_id: str,
    request: Request,
    admin: dict = Depends(require_dashboard_user),
    db: Session = Depends(get_db),
):
    approval_request = ApprovalRequest(
        message_id=message_id,
        approved=True,
        reviewer=admin.get("email", "dashboard-admin"),
        notes="Approved from dashboard.",
    )

    process_approval(
        request=approval_request,
        db=db,
    )

    return RedirectResponse(
        url="/dashboard",
        status_code=303,
    )


@app.post("/dashboard/reject/{message_id}")
def dashboard_reject_email(
    message_id: str,
    request: Request,
    admin: dict = Depends(require_dashboard_user),
    db: Session = Depends(get_db),
):
    approval_request = ApprovalRequest(
        message_id=message_id,
        approved=False,
        reviewer=admin.get("email", "dashboard-admin"),
        notes="Rejected from dashboard.",
    )

    process_approval(
        request=approval_request,
        db=db,
    )

    return RedirectResponse(
        url="/dashboard",
        status_code=303,
    )


@app.get("/login")
async def login(request: Request):
    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:8000/auth/callback",
    )

    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")

    if not user:
        user = await oauth.google.parse_id_token(request, token)

    email = user.get("email", "").lower()

    allowed_emails = {
        item.strip().lower()
        for item in os.getenv("ALLOWED_ADMIN_EMAILS", "").split(",")
        if item.strip()
    }

    if email not in allowed_emails:
        return RedirectResponse(url="/unauthorized")

    request.session["user"] = {
        "email": email,
        "name": user.get("name", ""),
        "picture": user.get("picture", ""),
    }

    return RedirectResponse(url="/dashboard")


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/unauthorized")
def unauthorized():
    return {
        "status": "unauthorized",
        "message": "This Google account is not authorized to access the dashboard.",
    }