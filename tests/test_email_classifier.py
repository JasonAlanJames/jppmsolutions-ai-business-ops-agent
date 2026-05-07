from app.email_ops.classifier import classify_email


def test_newsletter_archives_without_reply():
    result = classify_email(
        subject="Weekly update: new AI tools",
        sender="alerts@theresanaiforthat.com",
        body="Here are this week's new AI tools. Unsubscribe here.",
    )

    assert result.category == "archive"
    assert result.needs_reply is False


def test_account_billing_email_requires_human_review():
    result = classify_email(
        subject="Your OpenAI API account has been funded",
        sender="noreply@tm.openai.com",
        body="Your payment was successful and your API account has been funded.",
    )

    assert result.category == "human_review"
    assert result.priority == "high"


def test_customer_website_inquiry_needs_reply():
    result = classify_email(
        subject="Need a website and AI chatbot",
        sender="customer@example.com",
        body="Can you build a website and AI chatbot for my business? Please reply with next steps.",
    )

    assert result.category == "needs_reply"
    assert result.brand_route == "App & Web Developers"
    assert result.needs_reply is True


def test_printing_quote_routes_to_myprintingdeals():
    result = classify_email(
        subject="Need flyer printing quote",
        sender="customer@example.com",
        body="Can you give me a quote for 5000 flyers and EDDM direct mail?",
    )

    assert result.category == "needs_reply"
    assert result.brand_route == "MyPrintingDeals"


def test_spam_detected():
    result = classify_email(
        subject="Claim your prize now",
        sender="random@example.com",
        body="You won free money from the lottery.",
    )

    assert result.category == "spam"
    assert result.needs_reply is False