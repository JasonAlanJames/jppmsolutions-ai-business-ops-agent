import base64
import os
from email.mime.text import MIMEText
from typing import Any

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("GMAIL_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GMAIL_CLIENT_ID"),
        client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        scopes=GMAIL_SCOPES,
    )

    return build("gmail", "v1", credentials=creds)


def list_unread_emails(max_results: int = 10) -> list[dict[str, Any]]:
    service = get_gmail_service()

    response = (
        service.users()
        .messages()
        .list(userId="me", q="is:unread", maxResults=max_results)
        .execute()
    )

    return response.get("messages", [])


def get_email(message_id: str) -> dict[str, Any]:
    service = get_gmail_service()

    return (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )


def extract_headers(message: dict[str, Any]) -> dict[str, str]:
    headers = message.get("payload", {}).get("headers", [])

    return {
        header.get("name", "").lower(): header.get("value", "")
        for header in headers
    }


def extract_email_body(message: dict[str, Any]) -> str:
    payload = message.get("payload", {})

    def decode_part(part: dict[str, Any]) -> str:
        body = part.get("body", {})
        data = body.get("data")

        if not data:
            return ""

        decoded = base64.urlsafe_b64decode(data.encode("utf-8")).decode(
            "utf-8", errors="ignore"
        )

        return decoded

    if payload.get("body", {}).get("data"):
        return decode_part(payload)

    parts = payload.get("parts", [])

    for part in parts:
        if part.get("mimeType") == "text/plain":
            return decode_part(part)

    for part in parts:
        if part.get("mimeType") == "text/html":
            return decode_part(part)

    return message.get("snippet", "")


def create_draft_reply(
    to_email: str,
    subject: str,
    body: str,
    thread_id: str | None = None,
) -> dict[str, Any]:
    service = get_gmail_service()

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft_body: dict[str, Any] = {
        "message": {
            "raw": encoded_message,
        }
    }

    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    return service.users().drafts().create(userId="me", body=draft_body).execute()