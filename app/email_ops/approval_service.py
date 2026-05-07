from app.email_ops.approval_schemas import ApprovalRequest, ApprovalResult


APPROVAL_LOG: list[dict] = []


def process_approval(request: ApprovalRequest) -> ApprovalResult:
    APPROVAL_LOG.append(request.model_dump())

    if request.approved:
        return ApprovalResult(
            message_id=request.message_id,
            approved=True,
            reviewer=request.reviewer,
            notes=request.notes,
            action_taken="approved_for_draft",
            message="Email was approved for draft creation. No email was sent.",
        )

    return ApprovalResult(
        message_id=request.message_id,
        approved=False,
        reviewer=request.reviewer,
        notes=request.notes,
        action_taken="rejected",
        message="Email action was rejected. No draft or send action was performed.",
    )


def get_approval_log() -> list[dict]:
    return APPROVAL_LOG