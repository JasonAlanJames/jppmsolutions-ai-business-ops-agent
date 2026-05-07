from app.email_ops.approval_schemas import ApprovalRequest, ApprovalResult
from app.email_ops.gmail_client import (
    create_draft_reply,
    extract_email_body,
    extract_headers,
    get_email,
)
from app.email_ops.workflow_graph import run_email_workflow


APPROVAL_LOG: list[dict] = []


def process_approval(request: ApprovalRequest) -> ApprovalResult:
    approval_record = request.model_dump()
    APPROVAL_LOG.append(approval_record)

    if not request.approved:
        return ApprovalResult(
            message_id=request.message_id,
            approved=False,
            reviewer=request.reviewer,
            notes=request.notes,
            action_taken="rejected",
            message="Email action was rejected. No draft or send action was performed.",
        )

    message = get_email(request.message_id)
    headers = extract_headers(message)

    subject = headers.get("subject", "(No Subject)")
    sender = headers.get("from", "")
    reply_to = headers.get("reply-to") or sender
    body = extract_email_body(message)

    workflow_result = run_email_workflow(
        message_id=request.message_id,
        thread_id=message.get("threadId", ""),
        sender=sender,
        subject=subject,
        body=body,
    )

    if not workflow_result.get("needs_reply"):
        return ApprovalResult(
            message_id=request.message_id,
            approved=True,
            reviewer=request.reviewer,
            notes=request.notes,
            action_taken="no_action",
            message="Email was approved for review, but no draft was created because the workflow determined no reply is needed.",
        )

    draft = create_draft_reply(
        to_email=reply_to,
        subject=workflow_result.get("suggested_subject", f"Re: {subject}"),
        body=workflow_result.get("draft_reply", ""),
        thread_id=message.get("threadId"),
    )

    draft_id = draft.get("id", "")

    APPROVAL_LOG.append(
        {
            "message_id": request.message_id,
            "draft_id": draft_id,
            "action": "gmail_draft_created",
            "reviewer": request.reviewer,
            "notes": request.notes,
        }
    )

    return ApprovalResult(
        message_id=request.message_id,
        approved=True,
        reviewer=request.reviewer,
        notes=request.notes,
        action_taken="approved_for_draft",
        message=f"Gmail draft created successfully. Draft ID: {draft_id}. No email was sent.",
    )


def get_approval_log() -> list[dict]:
    return APPROVAL_LOG