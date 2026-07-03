import { ModalShell } from "./ModalShell"
import { RiskAnalysisPanel } from "./RiskAnalysisPanel"
import type { RiskAnalysisView } from "./riskAnalysis"

interface WarnModalProps {
  analysis: RiskAnalysisView
  onCancel: () => void
  onContinue: () => void
}

export function WarnModal({ analysis, onCancel, onContinue }: WarnModalProps) {
  return (
    <ModalShell
      tone="warn"
      title="Prompt contains sensitive information"
      subtitle="Review the details below before sending."
      footer={
        <>
          <button
            onClick={onCancel}
            className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
          >
            Cancel
          </button>
          <button
            onClick={onContinue}
            className="rounded-md bg-warning px-4 py-2 text-sm font-medium text-white hover:opacity-90"
          >
            Continue Anyway
          </button>
        </>
      }
    >
      <RiskAnalysisPanel analysis={analysis} />
    </ModalShell>
  )
}
