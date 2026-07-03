import { useSyncExternalStore } from "react"
import { WarnModal } from "./WarnModal"
import { BlockModal } from "./BlockModal"
import { RedactToast } from "./RedactToast"
import { dismiss, getState, subscribe } from "./store"

export function App() {
  const state = useSyncExternalStore(subscribe, getState)

  if (state.type === "warn") {
    return (
      <WarnModal
        analysis={state.analysis}
        onCancel={() => {
          state.onCancel()
          dismiss()
        }}
        onContinue={() => {
          state.onContinue()
          dismiss()
        }}
      />
    )
  }

  if (state.type === "block") {
    return <BlockModal analysis={state.analysis} onDismiss={dismiss} />
  }

  if (state.type === "redact-toast") {
    return <RedactToast message={state.message} onDismiss={dismiss} />
  }

  return null
}
