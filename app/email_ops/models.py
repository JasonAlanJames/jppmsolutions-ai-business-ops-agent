from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reviewer: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    action_taken: Mapped[str] = mapped_column(String(100), nullable=False)
    result_message: Mapped[str] = mapped_column(Text, nullable=False)
    draft_id: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class EmailWorkflowRecord(Base):
    __tablename__ = "email_workflow_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    thread_id: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    sender: Mapped[str] = mapped_column(Text, default="", nullable=False)
    subject: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    brand_route: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    needs_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    human_approval_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    draft_created: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    draft_id: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    audit_log: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )