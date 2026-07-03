/**
 * Shared DOM-watching logic used by every adapter (kept in one place per
 * "don't duplicate detection logic" - each adapter only supplies its own
 * selectors). Combines three redundant strategies, since these are
 * React/Angular SPAs that can remount the composer without a full
 * navigation:
 *
 *  1. MutationObserver on <body> - catches virtually all DOM changes.
 *  2. A cheap 1.5s poll - safety net for the rare mutation a observer misses.
 *  3. history.pushState/replaceState + popstate hooks - SPA route changes
 *     (e.g. opening a new chat) don't always trigger a body mutation
 *     immediately, so we explicitly re-check right after navigation.
 */
let historyPatched = false
const navigationListeners = new Set<() => void>()

function patchHistoryOnce() {
  if (historyPatched) return
  historyPatched = true

  const fire = () => navigationListeners.forEach((cb) => cb())

  const originalPushState = history.pushState.bind(history)
  history.pushState = (...args: Parameters<History["pushState"]>) => {
    originalPushState(...args)
    fire()
  }

  const originalReplaceState = history.replaceState.bind(history)
  history.replaceState = (...args: Parameters<History["replaceState"]>) => {
    originalReplaceState(...args)
    fire()
  }

  window.addEventListener("popstate", fire)
}

export function watchForComposer(
  findInput: () => HTMLElement | null,
  findSendButton: () => HTMLElement | null,
  onReady: (input: HTMLElement, sendButton: HTMLElement | null) => void
): MutationObserver {
  patchHistoryOnce()

  const seen = new WeakSet<HTMLElement>()
  const check = () => {
    const input = findInput()
    if (input && !seen.has(input)) {
      seen.add(input)
      onReady(input, findSendButton())
    }
  }

  const observer = new MutationObserver(check)
  observer.observe(document.body, { childList: true, subtree: true })

  const pollId = window.setInterval(check, 1500)
  navigationListeners.add(check)

  // MutationObserver has no built-in "stop everything" beyond disconnect(),
  // so piggyback the interval/nav-listener cleanup onto it.
  const originalDisconnect = observer.disconnect.bind(observer)
  observer.disconnect = () => {
    window.clearInterval(pollId)
    navigationListeners.delete(check)
    originalDisconnect()
  }

  check() // run once immediately in case the composer is already mounted
  return observer
}
