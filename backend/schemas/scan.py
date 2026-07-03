"""Pydantic schemas for POST /api/scan - the primary API the extension calls."""
from pydantic import BaseModel, Field, field_validator

# Milestone 6 hardening: the original schema had no cap on file count or
# attachment size, so a caller (or a compromised/buggy extension build)
# could send an arbitrarily large base64 payload and exhaust server memory
# decoding it - a simple, cheap DoS. These limits mirror what a real
# ChatGPT/Claude/Gemini attachment upload would realistically be.
MAX_FILES_PER_SCAN = 5
MAX_FILE_BASE64_LENGTH = 14_000_000  # ~10MB decoded (base64 is ~4/3 the size)


class ScanFileInput(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_base64: str = Field(..., max_length=MAX_FILE_BASE64_LENGTH)


class ScanRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=50_000)
    site: str = Field(..., description="ChatGPT | Claude | Gemini")
    files: list[ScanFileInput] = Field(default_factory=list, max_length=MAX_FILES_PER_SCAN)

    @field_validator("site")
    @classmethod
    def site_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("site must not be blank")
        return v


class TriggeredRule(BaseModel):
    detector: str
    severity: str
    score: int
    reason: str


class ScanResponse(BaseModel):
    # Field names kept stable from Milestone 1's extension contract
    # (decision / sanitized_prompt / findings) so the extension needs no
    # logic changes - only its request URL changes. risk/score/reason are
    # additive fields for the (future) Prompt Logs / Analytics dashboard.
    decision: str  # ALLOW | WARN | REDACT | BLOCK
    risk: str  # LOW | MEDIUM | HIGH | CRITICAL
    score: int
    reason: str
    sanitized_prompt: str
    findings: list[TriggeredRule] = []
