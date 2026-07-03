/**
 * Builds the "Explainable AI" view model from a ScanResult - the same
 * response object the backend already returns from POST /api/scan. No
 * backend changes; this is purely a presentation-layer transformation.
 */
import { extractTriggeredPolicy, friendlyDetectorName, splitFileSource } from "@/utils/labels"
import type { ScanResult } from "@/types/messages"

export interface RiskFindingView {
  title: string
  detail: string
  source: string | null
}

export interface RiskAnalysisView {
  risk: string
  score: number
  action: string
  reason: string
  triggeredPolicy: string | null
  findings: RiskFindingView[]
}

export function buildRiskAnalysis(result: ScanResult): RiskAnalysisView {
  const findings: RiskFindingView[] = (result.findings ?? []).map((f) => {
    const { source, text } = splitFileSource(f.reason)
    return {
      title: friendlyDetectorName(f.detector),
      detail: text,
      source,
    }
  })

  return {
    risk: result.risk ?? "MEDIUM",
    score: result.score ?? 0,
    action: result.decision,
    reason: result.reason ?? "This prompt was flagged by PromptShield AI.",
    triggeredPolicy: result.reason ? extractTriggeredPolicy(result.reason) : null,
    findings,
  }
}
