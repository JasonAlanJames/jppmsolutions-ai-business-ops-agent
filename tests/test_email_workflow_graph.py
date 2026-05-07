from app.email_ops.workflow_graph import run_email_workflow


def test_email_workflow_routes_printing_inquiry(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = run_email_workflow(
        message_id="test-message-1",
        thread_id="test-thread-1",
        sender="customer@example.com",
        subject="Need flyer printing quote",
        body="Can you give me a quote for 5000 flyers and EDDM direct mail?",
    )

    assert result["category"] == "needs_reply"
    assert result["brand_route"] == "MyPrintingDeals"
    assert result["action"] == "draft_reply_for_human_approval"
    assert result["human_approval_required"] is True
    assert len(result["audit_log"]) >= 4


def test_email_workflow_archives_newsletter(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = run_email_workflow(
        message_id="test-message-2",
        thread_id="test-thread-2",
        sender="newsletter@example.com",
        subject="Weekly product update",
        body="Here are our new features. Unsubscribe here.",
    )

    assert result["category"] == "archive"
    assert result["action"] == "review_for_archive"
    assert result["needs_reply"] is False
    assert result["human_approval_required"] is True


def test_email_workflow_requires_review_for_billing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = run_email_workflow(
        message_id="test-message-3",
        thread_id="test-thread-3",
        sender="noreply@google.com",
        subject="Your billing account has been terminated",
        body="Your billing account and account access require attention.",
    )

    assert result["category"] == "human_review"
    assert result["action"] == "human_review"
    assert result["human_approval_required"] is True