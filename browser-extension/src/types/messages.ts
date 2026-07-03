/**
 * Message contract shared between popup, content scripts, and the
 * background service worker. Kept as a single source of truth so all
 * three surfaces speak the same protocol.
 */
export type Decision = "ALLOW" | "WARN" | "REDACT" | "BLOCK"

export interface ScanFinding {
  detector: string
  severity: "NONE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  score: number
  reason: string
}

export interface ScanResult {
  decision: Decision
  // Added in Milestone 2 (AI Detection Engine) - populated by the Risk
  // Engine / Decision Engine. Optional so any older cached background
  // worker response still type-checks during rollout.
  risk?: "NONE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  score?: number
  reason?: string
  sanitized_prompt: string
  findings: ScanFinding[]
}

export interface AuthUser {
  id: string
  email: string
  full_name: string
  role: string
}

export type ExtensionMessage =
  | { type: "SCAN_PROMPT"; payload: { prompt: string; site: string } }
  | { type: "LOGIN"; payload: { email: string; password: string } }
  | { type: "LOGOUT" }
  | { type: "GET_AUTH_STATE" }
  | { type: "LOG_ACTIVITY"; payload: { site: string; decision: Decision } }
  | { type: "GET_BACKEND_STATUS" }
  | { type: "GET_PROTECTION_ENABLED" }
  | { type: "SET_PROTECTION_ENABLED"; payload: { enabled: boolean } }
  | { type: "GET_LAST_SCAN" }

export interface AuthState {
  isAuthenticated: boolean
  user: AuthUser | null
}

export interface BackendStatus {
  online: boolean
  lastCheckedAt: number | null
}

export interface LastScan {
  site: string
  decision: Decision
  at: number
}
