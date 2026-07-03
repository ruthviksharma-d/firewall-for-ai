"""
Pipeline Orchestrator - wires every stage of the AI Detection Engine
together in the order defined by the architecture doc:

  normalize -> regex -> presidio -> spacy -> source code -> company
  keyword -> secrets -> file scanner (per file, same detectors) ->
  semantic classifier (only if inconclusive) -> risk engine -> policy
  engine -> decision engine -> redactor

This is the single entrypoint routers/scan.py calls. No detection logic
lives in the router - it only handles HTTP concerns and auditing.
"""
import logging
from dataclasses import dataclass
from typing import Callable

from sqlalchemy.orm import Session

from ai.code_detector import detect_source_code
from ai.decision_engine import Decision, decide
from ai.file_scanner import extract_text_from_file
from ai.keyword_detector import detect_company_keywords
from ai.normalizer import normalize_prompt
from ai.policy_engine import evaluate_policies
from ai.presidio_detector import detect_presidio
from ai.regex_detector import detect_regex
from ai.risk_engine import assess_risk
from ai.secret_detector import detect_secrets_in_text
from ai.semantic_classifier import classify_semantic_risk, should_run_semantic_classifier
from ai.spacy_detector import detect_spacy
from schemas.detection import DetectionResult, Recommendation, Severity
from schemas.scan import ScanFileInput
from services.keyword_service import get_enabled_keywords
from services.policy_service import get_enabled_policies

logger = logging.getLogger("promptshield.ai.pipeline")


@dataclass
class PipelineOutput:
    decision: Decision
    sanitized_prompt: str
    all_results: list[DetectionResult]


def _safe_call(detector_name: str, fn: Callable[[], DetectionResult]) -> DetectionResult:
    """
    Milestone 6 hardening: every detector used to be called directly, so an
    unexpected exception in any ONE of them (a malformed-unicode edge case,
    a third-party library bug, anything not already caught internally)
    took down the entire /api/scan request with a 500 - no audit log entry,
    and a security tool that fails a *legitimate* prompt because of its own
    bug is worse than one that logs the failure and keeps scanning with the
    other eight detectors. This wraps every detector call so one broken
    detector degrades to a neutral result instead of failing the whole scan.
    """
    try:
        return fn()
    except Exception:
        logger.exception("Detector '%s' raised an unhandled exception - degrading to a neutral result.", detector_name)
        return DetectionResult(
            detector=detector_name,
            severity=Severity.NONE,
            score=0,
            matches=[],
            recommendation=Recommendation.ALLOW,
            reason=f"{detector_name} detector failed unexpectedly and was skipped for this scan.",
        )


def _run_deterministic_detectors(text: str, keywords: list[str]) -> list[DetectionResult]:
    """Regex -> Presidio -> spaCy -> Source Code -> Company Keyword -> Secrets."""
    return [
        _safe_call("regex", lambda: detect_regex(text)),
        _safe_call("presidio", lambda: detect_presidio(text)),
        _safe_call("spacy", lambda: detect_spacy(text)),
        _safe_call("source_code", lambda: detect_source_code(text)),
        _safe_call("company_keyword", lambda: detect_company_keywords(text, keywords)),
        _safe_call("secrets", lambda: detect_secrets_in_text(text)),
    ]


def _tag_with_source(results: list[DetectionResult], source_label: str) -> list[DetectionResult]:
    """Prefix each result's reason with its origin (e.g. an uploaded file) while
    keeping the DetectionResult schema itself identical across the board."""
    tagged = []
    for r in results:
        tagged.append(r.model_copy(update={"reason": f"[{source_label}] {r.reason}"}))
    return tagged


def run_pipeline(db: Session, prompt: str, site: str, files: list[ScanFileInput]) -> PipelineOutput:
    normalized = normalize_prompt(prompt)
    text = normalized.normalized

    keywords = get_enabled_keywords(db)

    all_results: list[DetectionResult] = list(_run_deterministic_detectors(text, keywords))

    # File Scanner: extract text, then run it through the SAME detector
    # pipeline (no duplicated detection logic), tagged by source filename.
    for file_input in files:
        extraction = extract_text_from_file(file_input.filename, file_input.content_base64)
        if not extraction.success or not extraction.text.strip():
            continue
        file_normalized = normalize_prompt(extraction.text).normalized
        file_results = _run_deterministic_detectors(file_normalized, keywords)
        all_results.extend(_tag_with_source(file_results, f"file:{file_input.filename}"))

    # OpenRouter Semantic Classifier - only when traditional detectors are
    # inconclusive. classify_semantic_risk() already fails open internally
    # (missing API key, network error, bad response all return a neutral
    # result - see semantic_classifier.py), but wrap it too for defense in
    # depth against a truly unexpected exception (e.g. a malformed response
    # body that survives its own try/except).
    if should_run_semantic_classifier(all_results):
        all_results.append(_safe_call("semantic", lambda: classify_semantic_risk(text)))

    risk_assessment = assess_risk(all_results)
    policies = get_enabled_policies(db)
    policy_outcome = evaluate_policies(all_results, policies)
    decision = decide(risk_assessment, policy_outcome, all_results)

    from ai.redactor import redact_text

    sanitized_prompt = redact_text(text, all_results)

    return PipelineOutput(decision=decision, sanitized_prompt=sanitized_prompt, all_results=all_results)
