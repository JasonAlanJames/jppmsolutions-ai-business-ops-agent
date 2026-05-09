from app.email_ops.approval_repository import (
    list_email_workflow_records,
    save_email_workflow_record,
    search_email_workflow_records,
    workflow_to_dict,
)


def test_save_email_workflow_record(db_session):
    record = save_email_workflow_record(
        db_session,
        message_id="test-message-persist-1",
        thread_id="test-thread-persist-1",
        sender="customer@example.com",
        subject="Need website help",
        category="needs_reply",
        brand_route="App & Web Developers",
        priority="medium",
        needs_reply=True,
        human_approval_required=True,
        action="draft_reply_for_human_approval",
        reason="Customer asked for website help.",
        draft_created=False,
        draft_id="",
        audit_log=["Workflow started.", "Classified email."],
    )

    assert record.id is not None
    assert record.message_id == "test-message-persist-1"
    assert record.brand_route == "App & Web Developers"
    assert record.needs_reply is True


def test_list_email_workflow_records(db_session):
    save_email_workflow_record(
        db_session,
        message_id="test-message-persist-2",
        thread_id="test-thread-persist-2",
        sender="customer@example.com",
        subject="Need AI automation",
        category="needs_reply",
        brand_route="App & Web Developers",
        priority="medium",
        needs_reply=True,
        human_approval_required=True,
        action="draft_reply_for_human_approval",
        reason="Customer asked for AI automation.",
        draft_created=False,
        draft_id="",
        audit_log=["Workflow started."],
    )

    records = list_email_workflow_records(db_session)

    assert len(records) >= 1
    assert records[0].message_id == "test-message-persist-2"


def test_workflow_to_dict(db_session):
    record = save_email_workflow_record(
        db_session,
        message_id="test-message-persist-3",
        thread_id="test-thread-persist-3",
        sender="customer@example.com",
        subject="Need printing quote",
        category="needs_reply",
        brand_route="MyPrintingDeals",
        priority="medium",
        needs_reply=True,
        human_approval_required=True,
        action="draft_reply_for_human_approval",
        reason="Customer asked for printing.",
        draft_created=False,
        draft_id="",
        audit_log=["Workflow started.", "Routed to MyPrintingDeals."],
    )

    data = workflow_to_dict(record)

    assert data["message_id"] == "test-message-persist-3"
    assert data["thread_id"] == "test-thread-persist-3"
    assert data["from"] == "customer@example.com"
    assert data["subject"] == "Need printing quote"
    assert data["brand_route"] == "MyPrintingDeals"
    assert data["needs_reply"] is True
    assert data["draft_created"] is False
    assert isinstance(data["audit_log"], list)
    assert "Routed to MyPrintingDeals." in data["audit_log"]

def test_search_email_workflow_records(db_session):
    save_email_workflow_record(
        db_session,
        message_id="test-message-search-1",
        thread_id="test-thread-search-1",
        sender="lead@example.com",
        subject="Need help with AI automation",
        category="needs_reply",
        brand_route="App & Web Developers",
        priority="high",
        needs_reply=True,
        human_approval_required=True,
        action="draft_reply_for_human_approval",
        reason="Lead asked about AI automation services.",
        draft_created=False,
        draft_id="",
        audit_log=["Workflow started.", "Matched AI automation search."],
    )

    results = search_email_workflow_records(
        db_session,
        query="AI automation",
    )

    assert len(results) >= 1
    assert results[0].message_id == "test-message-search-1"