from app.email_ops.llm_classifier import classify_email_with_llm
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

        triage = classify_email_with_llm(subject=subject, sender=sender, body=body)

        draft_id = None

        if create_drafts and triage.needs_reply and triage.human_approval_required:
            draft = create_draft_reply(
                to_email=reply_to,
                subject=triage.suggested_subject,
                body=triage.draft_reply,
                thread_id=message.get("threadId"),
            )
            draft_id = draft.get("id")

        results.append(
            {
                "message_id": item["id"],
                "thread_id": message.get("threadId"),
                "from": sender,
                "subject": subject,
                "category": triage.category,
                "brand_route": triage.brand_route,
                "priority": triage.priority,
                "needs_reply": triage.needs_reply,
                "human_approval_required": triage.human_approval_required,
                "reason": triage.reason,
                "draft_created": draft_id is not None,
                "draft_id": draft_id,
            }
        )

    return results


if __name__ == "__main__":
    output = triage_unread_emails(max_results=5, create_drafts=True)

    for item in output:
        print(item)