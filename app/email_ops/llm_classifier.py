import json
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.email_ops.classifier import classify_email as fallback_classify_email
from app.email_ops.schemas import EmailTriageResult

load_dotenv()

ALLOWED_BRANDS = {
    "JPPM Solutions",
    "AI Agent Innovation Academy",
    "App & Web Developers",
    "VLOGit Social Media",
    "MyPrintingDeals",
    "3D Figs",
    "SoCal Television",
    "World Television TV",
    "Tripping AI",
    "TapCard Digital Business Card",
    "Realty Media Expert",
    "USA Marketing NOW",
    "Useful AI Hacks",
}

SYSTEM_PROMPT = """
You are the email triage agent for JPPM Solutions.

Classify incoming emails safely and conservatively.

Categories:
- important
- needs_reply
- spam
- trash
- archive
- human_review

Rules:
- Never recommend sending automatically.
- Human approval is always required before any reply.
- Do not draft replies for archive, spam, or trash.
- If the email mentions billing, payments, API keys, login, account access, legal, refunds, contracts, or security, use human_review.
- If the email asks a real question, requests a quote, requests help, proposes partnership, requests sponsorship, or asks for services, use needs_reply.
- Newsletters, product updates, event announcements, CFPs, digest emails, and marketing emails from legitimate companies should usually be archive, not spam, unless they look malicious or scam-like.
- If unsure and the email appears business-critical, choose human_review. If unsure and it appears informational, automated, promotional, or newsletter-like, choose archive.

Brand routes:
- JPPM Solutions
- AI Agent Innovation Academy
- App & Web Developers
- VLOGit Social Media
- MyPrintingDeals
- 3D Figs
- SoCal Television
- World Television TV
- Tripping AI
- TapCard Digital Business Card
- Realty Media Expert
- USA Marketing NOW
- Useful AI Hacks

Return ONLY valid JSON:
{
  "category": "...",
  "brand_route": "...",
  "priority": "low|medium|high|critical",
  "needs_reply": true|false,
  "human_approval_required": true,
  "reason": "...",
  "suggested_subject": "...",
  "draft_reply": "..."
}
"""


def classify_email_with_llm(subject: str, sender: str, body: str) -> EmailTriageResult:
    if not os.getenv("OPENAI_API_KEY"):
        return fallback_classify_email(subject=subject, sender=sender, body=body)

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )

    user_prompt = f"""
Subject: {subject}
From: {sender}

Email body:
{body[:5000]}
"""

    try:
        response = llm.invoke(
            [
                ("system", SYSTEM_PROMPT),
                ("human", user_prompt),
            ]
        )

        raw = response.content.strip()
        parsed = json.loads(raw)

        parsed["human_approval_required"] = True

        if parsed.get("brand_route") not in ALLOWED_BRANDS:
            parsed["brand_route"] = fallback_classify_email(
                subject=subject,
                sender=sender,
                body=body,
            ).brand_route

        if parsed.get("category") in {"archive", "spam", "trash"}:
            parsed["needs_reply"] = False
            parsed["suggested_subject"] = ""
            parsed["draft_reply"] = ""

        return EmailTriageResult(**parsed)

    except Exception:
        return fallback_classify_email(subject=subject, sender=sender, body=body)