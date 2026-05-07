from pydantic import BaseModel, Field
from typing import Literal


class ApprovalRequest(BaseModel):
    message_id: str
    approved: bool
    reviewer: str = Field(default="Jason James")
    notes: str = ""


class ApprovalResult(BaseModel):
    message_id: str
    approved: bool
    reviewer: str
    notes: str
    action_taken: Literal["approved_for_draft", "rejected", "no_action"]
    message: str