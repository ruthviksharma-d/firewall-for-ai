"""
Audit Logger - the system of record for every prompt scanned. Writes an
AuditLog row and keeps the acting user's running prompt/violation counters
in sync (used by the Employees dashboard page in a later milestone).
"""
from sqlalchemy.orm import Session

from ai.decision_engine import Decision
from models.audit_log import AuditLog
from models.user import User
from schemas.detection import Recommendation


def log_scan(
    db: Session,
    user: User,
    site: str,
    original_prompt: str,
    sanitized_prompt: str,
    decision: Decision,
) -> AuditLog:
    entry = AuditLog(
        user_id=user.id,
        website=site,
        original_prompt=original_prompt,
        sanitized_prompt=sanitized_prompt,
        risk=decision.risk.value,
        score=decision.score,
        action=decision.action.value,
        reason=decision.reason,
        triggered_rules=decision.triggered_rules,
    )
    db.add(entry)

    user.prompt_count += 1
    if decision.action != Recommendation.ALLOW:
        user.violation_count += 1

    db.commit()
    db.refresh(entry)
    return entry
