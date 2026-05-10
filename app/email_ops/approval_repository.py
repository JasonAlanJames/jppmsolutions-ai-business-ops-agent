import json
from typing import Any

from sqlalchemy.orm import Session

from app.email_ops.models import ApprovalDecision, EmailWorkflowRecord


def save_approval_decision(
    db: Session,
    *,
    message_id: str,
    approved: bool,
    reviewer: str,
    notes: str,
    action_taken: str,
    result_message: str,
    draft_id: str = "",
) -> ApprovalDecision:
    record = ApprovalDecision(
        message_id=message_id,
        approved=approved,
        reviewer=reviewer,
        notes=notes,
        action_taken=action_taken,
        result_message=result_message,
        draft_id=draft_id,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_approval_decisions(db: Session, limit: int = 100) -> list[ApprovalDecision]:
    return (
        db.query(ApprovalDecision)
        .order_by(ApprovalDecision.created_at.desc())
        .limit(limit)
        .all()
    )


def save_email_workflow_record(
    db: Session,
    *,
    message_id: str,
    thread_id: str = "",
    sender: str = "",
    subject: str = "",
    category: str = "",
    brand_route: str = "",
    priority: str = "",
    needs_reply: bool = False,
    human_approval_required: bool = True,
    action: str = "",
    reason: str = "",
    draft_created: bool = False,
    draft_id: str = "",
    audit_log: list[str] | None = None,
) -> EmailWorkflowRecord:
    record = EmailWorkflowRecord(
        message_id=message_id,
        thread_id=thread_id,
        sender=sender,
        subject=subject,
        category=category,
        brand_route=brand_route,
        priority=priority,
        needs_reply=needs_reply,
        human_approval_required=human_approval_required,
        action=action,
        reason=reason,
        draft_created=draft_created,
        draft_id=draft_id,
        audit_log=json.dumps(audit_log or []),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_email_workflow_records(
    db: Session,
    limit: int = 100,
) -> list[EmailWorkflowRecord]:
    return (
        db.query(EmailWorkflowRecord)
        .order_by(EmailWorkflowRecord.created_at.desc())
        .limit(limit)
        .all()
    )


def search_email_workflow_records(
    db: Session,
    query: str,
    limit: int = 100,
) -> list[EmailWorkflowRecord]:
    search_term = f"%{query.strip()}%"

    return (
        db.query(EmailWorkflowRecord)
        .filter(
            EmailWorkflowRecord.subject.ilike(search_term)
            | EmailWorkflowRecord.sender.ilike(search_term)
            | EmailWorkflowRecord.category.ilike(search_term)
            | EmailWorkflowRecord.brand_route.ilike(search_term)
            | EmailWorkflowRecord.priority.ilike(search_term)
            | EmailWorkflowRecord.action.ilike(search_term)
            | EmailWorkflowRecord.reason.ilike(search_term)
        )
        .order_by(EmailWorkflowRecord.created_at.desc())
        .limit(limit)
        .all()
    )


def approval_to_dict(record: ApprovalDecision) -> dict[str, Any]:
    return {
        "id": record.id,
        "message_id": record.message_id,
        "approved": record.approved,
        "reviewer": record.reviewer,
        "notes": record.notes,
        "action_taken": record.action_taken,
        "result_message": record.result_message,
        "draft_id": record.draft_id,
        "created_at": record.created_at.isoformat(),
    }


def workflow_to_dict(record: EmailWorkflowRecord) -> dict[str, Any]:
    try:
        audit_log = json.loads(record.audit_log)
    except json.JSONDecodeError:
        audit_log = []

    return {
        "id": record.id,
        "message_id": record.message_id,
        "thread_id": record.thread_id,
        "from": record.sender,
        "subject": record.subject,
        "category": record.category,
        "brand_route": record.brand_route,
        "priority": record.priority,
        "needs_reply": record.needs_reply,
        "human_approval_required": record.human_approval_required,
        "action": record.action,
        "reason": record.reason,
        "draft_created": record.draft_created,
        "draft_id": record.draft_id,
        "audit_log": audit_log,
        "created_at": record.created_at.isoformat(),
    }

def get_email_workflow_record_by_message_id(
    db: Session,
    message_id: str,
) -> EmailWorkflowRecord | None:
    return (
        db.query(EmailWorkflowRecord)
        .filter(EmailWorkflowRecord.message_id == message_id)
        .order_by(EmailWorkflowRecord.created_at.desc())
        .first()
    )

def list_approval_decisions_for_message(
    db: Session,
    message_id: str,
    limit: int = 50,
) -> list[ApprovalDecision]:
    return (
        db.query(ApprovalDecision)
        .filter(ApprovalDecision.message_id == message_id)
        .order_by(ApprovalDecision.created_at.desc())
        .limit(limit)
        .all()
    )