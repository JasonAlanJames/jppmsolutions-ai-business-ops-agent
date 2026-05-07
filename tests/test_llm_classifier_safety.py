import os

from app.email_ops.llm_classifier import ALLOWED_BRANDS, classify_email_with_llm


def test_allowed_brands_contains_only_jppm_routes():
    assert "JPPM Solutions" in ALLOWED_BRANDS
    assert "App & Web Developers" in ALLOWED_BRANDS
    assert "Google Cloud Platform" not in ALLOWED_BRANDS


def test_llm_classifier_falls_back_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = classify_email_with_llm(
        subject="Need flyer printing quote",
        sender="customer@example.com",
        body="Can you give me a quote for 5000 flyers and EDDM direct mail?",
    )

    assert result.brand_route == "MyPrintingDeals"
    assert result.category == "needs_reply"
    assert result.human_approval_required is True


def test_archive_emails_do_not_generate_drafts_without_llm(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = classify_email_with_llm(
        subject="Weekly product update",
        sender="newsletter@example.com",
        body="Here are our new features. Unsubscribe here.",
    )

    assert result.category == "archive"
    assert result.needs_reply is False
    assert result.draft_reply == ""


def test_sensitive_email_requires_human_review_without_llm(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = classify_email_with_llm(
        subject="Your billing account has been terminated",
        sender="noreply@google.com",
        body="Your billing account and account access require attention.",
    )

    assert result.category == "human_review"
    assert result.human_approval_required is True
    assert result.needs_reply is False