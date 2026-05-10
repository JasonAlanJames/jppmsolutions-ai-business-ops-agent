from app.email_ops.gmail_search import search_gmail_messages


def test_search_gmail_messages_empty_query_returns_empty_list():
    results = search_gmail_messages("")

    assert results == []


def test_search_gmail_messages_whitespace_query_returns_empty_list():
    results = search_gmail_messages("   ")

    assert results == []