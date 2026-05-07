from app.email_ops.workflow_graph import run_email_workflow
from app.email_ops.gmail_client import (
    create_draft_reply,
    extract_email_body,
    extract_headers,
    get_email,
    list_unread_emails,
)


def triage_unread_emails(max_results: int = 5, create_drafts: bool = False):
    messages = list_unread_emails(max_results=max_results)
    results = []

    for item in messages:
        message = get_email(item["id"])
        headers = extract_headers(message)

        subject = headers.get("subject", "(No Subject)")
        sender = headers.get("from", "")
        reply_to = headers.get("reply-to") or sender
        body = extract_email_body(message)

        workflow_result = run_email_workflow(
            message_id=item["id"],
            thread_id=message.get("threadId", ""),
            sender=sender,
            subject=subject,
            body=body,
        )

        draft_id = None

        if (
            create_drafts
            and workflow_result.get("needs_reply")
            and workflow_result.get("human_approval_required")
        ):
            draft = create_draft_reply(
                to_email=reply_to,
                subject=workflow_result.get("suggested_subject", f"Re: {subject}"),
                body=workflow_result.get("draft_reply", ""),
                thread_id=message.get("threadId"),
            )
            draft_id = draft.get("id")

        results.append(
            {
                "message_id": item["id"],
                "thread_id": message.get("threadId"),
                "from": sender,
                "subject": subject,
                "category": workflow_result.get("category"),
                "brand_route": workflow_result.get("brand_route"),
                "priority": workflow_result.get("priority"),
                "needs_reply": workflow_result.get("needs_reply"),
                "human_approval_required": workflow_result.get("human_approval_required"),
                "reason": workflow_result.get("reason"),
                "action": workflow_result.get("action"),
                "audit_log": workflow_result.get("audit_log", []),
                "draft_created": draft_id is not None,
                "draft_id": draft_id,
            }
        )

    return results


if __name__ == "__main__":
    output = triage_unread_emails(max_results=5, create_drafts=False)

    for item in output:
        print(item)