/**
 * Minimal external store for the content-script UI. A single React root is
 * mounted once per page (see mount.tsx); everything else - showing a WARN
 * modal, a BLOCK modal, or a REDACT toast - just calls into this store, and
 * App.tsx re-renders via useSyncExternalStore. Keeps the imperative
 * interception logic in content/index.ts decoupled from React.
 */
import type { RiskAnalysisView } from "./riskAnalysis"

export type UIState =
  | { type: "idle" }
  | { type: "warn"; analysis: RiskAnalysisView; onCancel: () => void; onContinue: () => void }
  | { type: "block"; analysis: RiskAnalysisView }
  | { type: "redact-toast"; message: string }

let state: UIState = { type: "idle" }
const listeners = new Set<() => void>()

export function getState(): UIState {
  return state
}

export function setState(next: UIState): void {
  state = next
  listeners.forEach((listener) => listener())
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function dismiss(): void {
  setState({ type: "idle" })
}
