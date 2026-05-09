from typing import Any

from sqlalchemy.orm import Session

from app.email_ops.approval_repository import save_email_workflow_record
from app.email_ops.gmail_client import (
    create_draft_reply,
    extract_email_body,
    extract_headers,
    get_email,
    list_unread_emails,
)
from app.email_ops.workflow_graph import run_email_workflow


def triage_unread_emails(
    max_results: int = 5,
    create_drafts: bool = False,
    db: Session | None = None,
) -> list[dict[str, Any]]:
    """
    Triage unread Gmail messages through the LangGraph workflow.

    Safe defaults:
    - create_drafts=False
    - no email is sent automatically
    - workflow records are persisted only when db is provided
    """
    messages = list_unread_emails(max_results=max_results)
    results: list[dict[str, Any]] = []

    for item in messages:
        message_id = item["id"]
        message = get_email(message_id)
        headers = extract_headers(message)

        thread_id = message.get("threadId", "")
        subject = headers.get("subject", "(No Subject)")
        sender = headers.get("from", "")
        reply_to = headers.get("reply-to") or sender
        body = extract_email_body(message)

        workflow_result = run_email_workflow(
            message_id=message_id,
            thread_id=thread_id,
            sender=sender,
            subject=subject,
            body=body,
        )

        draft_id = ""

        if (
            create_drafts
            and workflow_result.get("needs_reply")
            and workflow_result.get("human_approval_required")
        ):
            draft = create_draft_reply(
                to_email=reply_to,
                subject=workflow_result.get("suggested_subject", f"Re: {subject}"),
                body=workflow_result.get("draft_reply", ""),
                thread_id=thread_id,
            )
            draft_id = draft.get("id", "")

        result = {
            "message_id": message_id,
            "thread_id": thread_id,
            "from": sender,
            "subject": subject,
            "category": workflow_result.get("category", ""),
            "brand_route": workflow_result.get("brand_route", ""),
            "priority": workflow_result.get("priority", ""),
            "needs_reply": bool(workflow_result.get("needs_reply", False)),
            "human_approval_required": bool(
                workflow_result.get("human_approval_required", True)
            ),
            "reason": workflow_result.get("reason", ""),
            "action": workflow_result.get("action", ""),
            "audit_log": workflow_result.get("audit_log", []),
            "draft_created": bool(draft_id),
            "draft_id": draft_id,
        }

        if db is not None:
            save_email_workflow_record(
                db,
                message_id=result["message_id"],
                thread_id=result["thread_id"],
                sender=result["from"],
                subject=result["subject"],
                category=result["category"],
                brand_route=result["brand_route"],
                priority=result["priority"],
                needs_reply=result["needs_reply"],
                human_approval_required=result["human_approval_required"],
                action=result["action"],
                reason=result["reason"],
                draft_created=result["draft_created"],
                draft_id=result["draft_id"],
                audit_log=result["audit_log"],
            )

        results.append(result)

    return results


if __name__ == "__main__":
    output = triage_unread_emails(
        max_results=5,
        create_drafts=False,
    )

    for item in output:
        print(item)