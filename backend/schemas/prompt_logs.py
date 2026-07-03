"""Schemas for GET /api/prompt-logs (list) and GET /api/prompt-logs/{id} (detail)."""
from datetime import datetime

from pydantic import BaseModel


class PromptLogListItem(BaseModel):
    id: str
    employee_name: str
    employee_email: str
    website: str
    risk: str
    score: int
    action: str
    status: str  # "Clean" | "Flagged" - derived from action
    created_at: datetime


class PromptLogListResponse(BaseModel):
    items: list[PromptLogListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TriggeredRuleDetail(BaseModel):
    detector: str
    severity: str
    score: int
    reason: str


class PromptLogDetail(BaseModel):
    id: str
    employee_name: str
    employee_email: str
    department: str | None
    website: str
    risk: str
    score: int
    action: str
    reason: str
    triggered_policy: str | None
    original_prompt: str
    sanitized_prompt: str
    triggered_rules: list[TriggeredRuleDetail]
    created_at: datetime
