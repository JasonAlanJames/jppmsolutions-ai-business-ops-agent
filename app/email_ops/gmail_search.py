from typing import Any

from app.email_ops.gmail_client import extract_headers, get_email, get_gmail_service


def search_gmail_messages(
    query: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """
    Search Gmail using Gmail query syntax.

    Examples:
    - AI automation
    - from:customer@example.com
    - subject:invoice
    - newer_than:30d
    """
    if not query.strip():
        return []

    service = get_gmail_service()

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=query,
            maxResults=max_results,
        )
        .execute()
    )

    messages = response.get("messages", [])
    results: list[dict[str, Any]] = []

    for item in messages:
        message = get_email(item["id"])
        headers = extract_headers(message)

        results.append(
            {
                "message_id": item["id"],
                "thread_id": message.get("threadId", ""),
                "from": headers.get("from", ""),
                "subject": headers.get("subject", "(No Subject)"),
                "date": headers.get("date", ""),
                "snippet": message.get("snippet", ""),
            }
        )

    return results