from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.email_ops.llm_classifier import classify_email_with_llm


class EmailWorkflowState(TypedDict, total=False):
    message_id: str
    thread_id: str
    sender: str
    subject: str
    body: str

    category: str
    brand_route: str
    priority: str
    needs_reply: bool
    human_approval_required: bool
    reason: str
    suggested_subject: str
    draft_reply: str

    action: str
    audit_log: list[str]


def initialize_state(state: EmailWorkflowState) -> dict[str, Any]:
    return {
        "audit_log": [
            "Workflow started.",
            f"Received email from {state.get('sender', 'unknown sender')}.",
        ]
    }


def classify_and_route(state: EmailWorkflowState) -> dict[str, Any]:
    triage = classify_email_with_llm(
        subject=state.get("subject", ""),
        sender=state.get("sender", ""),
        body=state.get("body", ""),
    )

    audit_log = state.get("audit_log", [])
    audit_log.append(
        f"Classified email as {triage.category} routed to {triage.brand_route}."
    )

    return {
        "category": triage.category,
        "brand_route": triage.brand_route,
        "priority": triage.priority,
        "needs_reply": triage.needs_reply,
        "human_approval_required": triage.human_approval_required,
        "reason": triage.reason,
        "suggested_subject": triage.suggested_subject,
        "draft_reply": triage.draft_reply,
        "audit_log": audit_log,
    }


def decide_next_action(state: EmailWorkflowState) -> dict[str, Any]:
    category = state.get("category")
    needs_reply = state.get("needs_reply", False)

    if category in {"spam", "trash"}:
        action = "review_for_removal"
    elif category == "archive":
        action = "review_for_archive"
    elif needs_reply:
        action = "draft_reply_for_human_approval"
    else:
        action = "human_review"

    audit_log = state.get("audit_log", [])
    audit_log.append(f"Next action selected: {action}.")

    return {
        "action": action,
        "audit_log": audit_log,
    }


def prepare_human_review(state: EmailWorkflowState) -> dict[str, Any]:
    audit_log = state.get("audit_log", [])
    audit_log.append("Human approval required before any external action.")

    return {
        "human_approval_required": True,
        "audit_log": audit_log,
    }


def route_after_decision(state: EmailWorkflowState) -> str:
    return "human_review"


def build_email_triage_graph():
    graph = StateGraph(EmailWorkflowState)

    graph.add_node("initialize_state", initialize_state)
    graph.add_node("classify_and_route", classify_and_route)
    graph.add_node("decide_next_action", decide_next_action)
    graph.add_node("human_review", prepare_human_review)

    graph.add_edge(START, "initialize_state")
    graph.add_edge("initialize_state", "classify_and_route")
    graph.add_edge("classify_and_route", "decide_next_action")
    graph.add_conditional_edges(
        "decide_next_action",
        route_after_decision,
        {
            "human_review": "human_review",
        },
    )
    graph.add_edge("human_review", END)

    return graph.compile()


email_triage_graph = build_email_triage_graph()


def run_email_workflow(
    message_id: str,
    thread_id: str,
    sender: str,
    subject: str,
    body: str,
) -> EmailWorkflowState:
    return email_triage_graph.invoke(
        {
            "message_id": message_id,
            "thread_id": thread_id,
            "sender": sender,
            "subject": subject,
            "body": body,
        }
    )