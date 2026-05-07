from typing import Literal

from pydantic import BaseModel, Field


EmailCategory = Literal[
    "important",
    "needs_reply",
    "spam",
    "trash",
    "archive",
    "human_review",
]


class EmailTriageResult(BaseModel):
    category: EmailCategory
    brand_route: str = Field(description="Best JPPM brand or subsidiary route.")
    priority: Literal["low", "medium", "high", "critical"]
    needs_reply: bool
    human_approval_required: bool = True
    reason: str
    suggested_subject: str
    draft_reply: str