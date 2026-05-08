from app.email_ops.reply_generator import generate_rag_reply
from app.email_ops.workflow_graph import run_email_workflow


def test_reply_generator_fallback_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    reply = generate_rag_reply(
        subject="Need flyer printing quote",
        sender="customer@example.com",
        body="Can you give me a quote for 5000 flyers and EDDM direct mail?",
        brand_route="MyPrintingDeals",
    )

    assert "Thank you for reaching out" in reply
    assert "MyPrintingDeals" in reply


def test_workflow_generates_draft_for_customer_inquiry(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = run_email_workflow(
        message_id="test-message-4",
        thread_id="test-thread-4",
        sender="customer@example.com",
        subject="Need website and AI chatbot",
        body="Can you build a website and AI chatbot for my business? Please reply with next steps.",
    )

    assert result["category"] == "needs_reply"
    assert result["brand_route"] == "App & Web Developers"
    assert result["action"] == "draft_reply_for_human_approval"
    assert "Thank you for reaching out" in result["draft_reply"]
    assert result["human_approval_required"] is True