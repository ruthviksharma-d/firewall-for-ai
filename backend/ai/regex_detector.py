"""
Regex Detector - fast, deterministic pattern matching for structured
sensitive data: emails, phone numbers, credit cards, API keys, JWTs, cloud
provider credentials, and URLs. Runs first because it's cheap and catches
the highest-confidence, highest-severity findings (live secrets) before
any NLP model has to run.
"""
import re

from schemas.detection import SEVERITY_RANK, DetectionResult, Match, Recommendation, Severity

# (label, pattern, severity, score-per-match)
_PATTERNS: list[tuple[str, re.Pattern, Severity, int]] = [
    ("EMAIL", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), Severity.LOW, 8),
    (
        "PHONE_NUMBER",
        re.compile(r"(?<!\d)(\+?\d{1,3}[-.\s]?)?(\(?\d{3,4}\)?[-.\s]?)\d{3}[-.\s]?\d{3,4}(?!\d)"),
        Severity.LOW,
        6,
    ),
    ("CREDIT_CARD", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), Severity.HIGH, 30),
    ("AWS_ACCESS_KEY", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"), Severity.CRITICAL, 45),
    ("AWS_SECRET_KEY", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?"), Severity.CRITICAL, 45),
    ("GITHUB_TOKEN", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"), Severity.CRITICAL, 45),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), Severity.CRITICAL, 40),
    ("OPENAI_API_KEY", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), Severity.CRITICAL, 40),
    (
        "JWT_TOKEN",
        re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
        Severity.HIGH,
        35,
    ),
    (
        "GENERIC_API_KEY",
        re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"]?[A-Za-z0-9\-_]{16,}['\"]?"),
        Severity.HIGH,
        30,
    ),
    (
        "PASSWORD",
        re.compile(r"(?i)\b(password|passwd|pwd)\b\s*[:=]\s*['\"]?\S{4,}['\"]?"),
        Severity.HIGH,
        25,
    ),
    ("URL", re.compile(r"https?://[^\s<>\"']+"), Severity.NONE, 2),
]


def _luhn_valid(digits: str) -> bool:
    total = 0
    reverse_digits = digits[::-1]
    for i, ch in enumerate(reverse_digits):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _mask(value: str, label: str) -> str:
    digits_only = re.sub(r"\D", "", value)
    if label in {"CREDIT_CARD", "PHONE_NUMBER"} and len(digits_only) >= 4:
        return f"****{digits_only[-4:]}"
    if len(value) <= 8:
        return value[0] + "*" * (len(value) - 1)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def detect_regex(text: str) -> DetectionResult:
    matches: list[Match] = []
    total_score = 0
    highest_severity = Severity.NONE
    hit_labels: set[str] = set()

    for label, pattern, severity, score in _PATTERNS:
        for m in pattern.finditer(text):
            value = m.group(0)

            if label == "CREDIT_CARD":
                digits = re.sub(r"\D", "", value)
                if not (13 <= len(digits) <= 19) or not _luhn_valid(digits):
                    continue

            matches.append(
                Match(label=label, value_preview=_mask(value, label), start=m.start(), end=m.end())
            )
            total_score += score
            hit_labels.add(label)
            if SEVERITY_RANK[severity] > SEVERITY_RANK[highest_severity]:
                highest_severity = severity

    total_score = min(total_score, 100)

    if not matches:
        return DetectionResult(
            detector="regex",
            severity=Severity.NONE,
            score=0,
            matches=[],
            recommendation=Recommendation.ALLOW,
            reason="No regex-matched patterns found.",
        )

    critical_hit = any(
        label in {"AWS_ACCESS_KEY", "AWS_SECRET_KEY", "GITHUB_TOKEN", "GOOGLE_API_KEY", "OPENAI_API_KEY", "GENERIC_API_KEY"}
        for label in hit_labels
    )
    recommendation = (
        Recommendation.BLOCK
        if critical_hit
        else Recommendation.REDACT
        if highest_severity in {Severity.HIGH, Severity.MEDIUM}
        else Recommendation.WARN
        if highest_severity == Severity.LOW
        else Recommendation.ALLOW
    )

    return DetectionResult(
        detector="regex",
        severity=highest_severity,
        score=total_score,
        matches=matches,
        recommendation=recommendation,
        reason=f"Matched: {', '.join(sorted(hit_labels))}.",
    )
