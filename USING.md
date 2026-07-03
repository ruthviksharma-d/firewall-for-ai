# Using PromptShield AI

This is a step-by-step usage guide for PromptShield AI, written for the people
who will actually run it day to day: the security/IT admin who configures it,
and the employees who use it without thinking about it. If you're looking for
installation instructions instead, see [`README.md`](README.md) — this guide
assumes the backend, admin dashboard, and browser extension are already
running.

---

## Table of Contents

1. [What PromptShield AI Is](#what-promptshield-ai-is)
2. [The Three Things You're Running](#the-three-things-youre-running)
3. [Signing In](#signing-in)
4. [Using the Admin Dashboard](#using-the-admin-dashboard)
   - [Dashboard page](#dashboard-page)
   - [Prompt Logs page](#prompt-logs-page)
   - [Policies page](#policies-page)
   - [Employees page](#employees-page)
   - [Analytics page](#analytics-page)
   - [Settings page](#settings-page)
5. [Using the Browser Extension](#using-the-browser-extension)
   - [Installing it in Chrome](#installing-it-in-chrome)
   - [Signing in from the popup](#signing-in-from-the-popup)
   - [What the popup shows you](#what-the-popup-shows-you)
   - [What happens when you type a prompt](#what-happens-when-you-type-a-prompt)
   - [Reading the Explainable AI panel](#reading-the-explainable-ai-panel)
6. [Common Workflows, Step by Step](#common-workflows-step-by-step)
   - [Workflow: onboarding a new employee](#workflow-onboarding-a-new-employee)
   - [Workflow: writing your first policy](#workflow-writing-your-first-policy)
   - [Workflow: investigating a blocked prompt](#workflow-investigating-a-blocked-prompt)
   - [Workflow: adding a company keyword](#workflow-adding-a-company-keyword)
   - [Workflow: temporarily pausing protection](#workflow-temporarily-pausing-protection)
   - [Workflow: reviewing weekly risk trends](#workflow-reviewing-weekly-risk-trends)
7. [Understanding the Four Decisions](#understanding-the-four-decisions)
8. [Troubleshooting](#troubleshooting)
9. [Demo Credentials Reference](#demo-credentials-reference)

---

## What PromptShield AI Is

PromptShield AI is an AI firewall for organizations whose employees use
ChatGPT, Claude, and Gemini in their day-to-day work. It doesn't ask anyone to
stop using those tools or switch to a different one. Instead, it sits quietly
between the employee and the AI website: every time someone types a prompt and
hits send, PromptShield inspects it first, decides whether it's safe, and only
then lets it (or a cleaned-up version of it) reach the AI.

It's made of three parts that you'll interact with differently:

- **A browser extension** — this is what employees see (or, most of the time,
  don't see, because it's silent unless it finds something).
- **An admin dashboard** — this is what security/IT teams use to watch
  activity, write rules, and investigate incidents.
- **A backend** — you don't interact with this directly; it's the engine
  running underneath both of the above.

This guide covers the first two, since those are the parts with an actual
interface.

## The Three Things You're Running

Before you start, make sure you know:

- The **dashboard URL** you were given (locally, this is
  `http://localhost:5173`).
- The **backend URL** the extension is configured to talk to (locally,
  `http://localhost:8000` — you don't need to open this in a browser, the
  extension talks to it automatically).
- Your **login email and password** (an admin should have given you these; if
  you're the admin setting this up yourself for the first time, see
  [Demo Credentials Reference](#demo-credentials-reference)).

## Signing In

Both the dashboard and the extension use the same account system, so the same
email and password work in both places — but you sign in to them separately.

**Dashboard:**
1. Open the dashboard URL in your browser.
2. You'll land on the marketing landing page. Click **Sign in** in the
   top-right corner (or go straight to `/login`).
3. Enter your email and password, then click **Sign in**.
4. You're taken to the Dashboard page.

**Extension:** see [Signing in from the popup](#signing-in-from-the-popup)
below — it's a separate login step because the extension and the dashboard
run in different browser contexts and don't share a session automatically.

If your session expires (access tokens last 60 minutes by default), both
surfaces will drop you back to a sign-in screen — just log in again, nothing
is lost.

---

## Using the Admin Dashboard

The dashboard has six pages, listed in the left sidebar: **Dashboard**,
**Prompt Logs**, **Policies**, **Employees**, **Analytics**, and **Settings**.
Every number, table, and chart on every page is a live query against your
organization's real scan history — there's nothing hardcoded or fake, so an
empty dashboard on day one is expected and will fill in as employees start
using the extension.

Note: Dashboard, Prompt Logs, Policies, Employees, and Analytics require an
**admin** or **security_analyst** account. Policy, Settings, and keyword
changes additionally require **admin** specifically — if you're signed in as
a security_analyst, you'll be able to view everything but write actions will
be blocked.

### Dashboard page

This is your home screen — a one-glance summary of your organization's AI
usage and risk posture. It shows:

- **Eight summary cards** across the top: Security Score (out of 100),
  Total Prompts, Allowed, Warned, Redacted, Blocked, Active Employees, and
  Protected AI Websites.
- **A daily activity chart** — how many prompts were allowed/warned/
  redacted/blocked each day, so you can spot a spike immediately.
- **A risk distribution breakdown** — how many scans fell into each risk
  band (None/Low/Medium/High/Critical).
- **Top violation types** — which detectors are firing most often across
  your organization (e.g. "company_keyword" or "regex").
- **A recent activity feed** — the most recent scans, each showing who
  triggered it, which website, what action was taken, and when.

If there's no data yet, you'll see an empty state explaining that scans will
appear here once employees start using the extension — this is normal for a
freshly-installed deployment.

**What to do here:** check this page first thing each day or each week. If
the Security Score drops or Blocked count spikes, that's your cue to go look
at Prompt Logs for the specifics.

### Prompt Logs page

This is your investigation tool — every single scan, individually.

1. At the top, you have a **search box** (searches by employee name or
   email) and **filter dropdowns** for Action (Allow/Warn/Redact/Block),
   Risk (None/Low/Medium/High/Critical), and AI Website (ChatGPT/Claude/
   Gemini). Filters combine — you can search for one employee AND filter to
   only their Blocked prompts.
2. The table shows: Employee, AI Website, Risk, a sortable Score column, the
   Action taken, a sortable timestamp, and a Status indicator.
3. **Click any row** to open a detail drawer on the right side. This shows:
   - The original prompt the employee typed (masked by default — click the
     eye icon to reveal it, since this is sensitive data).
   - The sanitized/redacted version that was actually sent, if applicable.
   - Every individual detector finding (which detector fired, at what
     severity, and why).
   - The specific policy that was triggered, if a policy (rather than the
     default risk-based behavior) decided the outcome.
4. Use the **pagination controls** at the bottom to move through pages of
   results (15 per page).
5. Click **Reset** next to the filters to clear everything and start over.

**What to do here:** this is where you go when you already know something
happened and need the details — either because the Dashboard showed a spike,
an employee reported something, or you're doing a periodic audit.

### Policies page

This is where you define what PromptShield actually does when it finds
something. Without any policies, PromptShield falls back to a default
severity-based behavior (low risk = allow, medium = warn, high = redact,
critical = block) — policies let you override that with explicit rules.

1. Click **New Policy** (or the **+** button) to open the policy form.
2. Fill in:
   - **Name** — a short label, e.g. "Block API Keys".
   - **Description** — what this policy does, for your own team's reference.
   - **Priority** — a number; **lower numbers are evaluated first**. If two
     enabled policies could both apply to the same prompt, the one with the
     lower priority number wins.
   - **Action** — what to do when this policy matches: Allow, Warn, Redact,
     or Block.
   - **Detection Type** — what kind of finding triggers this policy. You can
     pick something specific (API Key, Password, Email Address, Phone
     Number, Credit Card, JWT Token, SSH Key/Certificate, Personal
     Information (PII), Source Code, Company Keyword) or something broad
     (Any Leaked Credential, Any Regex Match, Any PII Match, AI Semantic
     Risk, or Any Detection at all).
   - **Enabled** — toggle this off to keep a policy defined but inactive,
     without deleting it.
3. Click **Create Policy** (or **Save Changes** if editing).
4. To edit an existing policy, click the pencil icon on its row. To delete
   one, click the trash icon and confirm in the dialog that appears.
5. The table shows every policy sorted by priority, with its detection type,
   action, and an enable/disable toggle you can flip directly from the row
   without opening the full form.

**What to do here:** start narrow and specific ("Block AI-detected API
keys") before writing broad catch-all rules, so you can see the effect of
each policy individually in Prompt Logs before layering on more.

### Employees page

Your organization's directory, from a security lens.

1. Use the **search box** (name or email) and the **Department** free-text
   filter and **Role** dropdown to narrow the list.
2. The table shows: Name, Department, Role, Total Prompts, Violations (any
   non-Allow scan), Last Active, and an Extension status badge.
3. The **Extension status** badge (Active / Inactive / Not Installed) is
   computed automatically from real scan activity — nobody has to manually
   mark an employee as "protected." Active means they've scanned a prompt
   in roughly the last day; Inactive means they have scanned before but not
   recently; Not Installed means no scan has ever been recorded for them.

**What to do here:** use this to spot employees who show as "Not Installed"
(meaning they likely haven't set up the extension yet) or employees with a
high violation count relative to their peers (worth a quiet conversation,
not necessarily a punitive one).

### Analytics page

Deeper trend charts for reporting and pattern-spotting, built from the same
underlying data as the Dashboard page but sliced differently:

- **Daily Prompt Usage** — volume over time.
- **Blocked vs Allowed** — the split, over time.
- **Risk Trend** — average risk score per day, so you can see whether things
  are trending safer or riskier.
- **Top Triggered Rules** — which specific detectors fire most often.
- **Website Usage** — ChatGPT vs Claude vs Gemini split.
- **Department Usage** — which teams are generating the most AI traffic.
- **Top Employees by Violations** — a ranked list, useful for targeted
  training conversations.

**What to do here:** pull this up before a monthly security review or when
building a report for leadership — it's designed to answer "what's our AI
usage trend" rather than "what happened in this one incident" (that's Prompt
Logs).

### Settings page

Organization-wide configuration, admin-only.

1. **Organization name** — shown in reports and (in a future version) in
   emails.
2. **Risk threshold (0-100)** — an informational threshold for your own
   reference; it doesn't currently change detection behavior directly, but
   marks the score your team considers "concerning" for reporting purposes.
3. **Supported AI websites** — which sites the extension is expected to
   protect (ChatGPT, Claude, Gemini).
4. **Allowed file types** — which attachment types the File Scanner will
   process (pdf, docx, csv, xlsx, txt, png, jpg, jpeg by default).
5. **Company Keywords** — a list of sensitive internal terms (project
   codenames, classification labels, anything specific to your org) that the
   Company Keyword Detector watches for. Type a keyword into the box and
   click **Add**; click the **X** next to any keyword to remove it, or use
   the toggle to disable it without deleting it.

**What to do here:** this is usually a one-time setup step when you first
deploy PromptShield, revisited only when you add a new confidential project
codename to the Company Keywords list.

---

## Using the Browser Extension

### Installing it in Chrome

1. Go to `chrome://extensions`.
2. Turn on **Developer mode** using the toggle in the top-right corner.
3. Click **Load unpacked**.
4. Select the `browser-extension/dist` folder (this is the built extension —
   see the README's "Loading the Browser Extension" section if this folder
   doesn't exist yet).
5. You'll see the PromptShield AI shield icon appear in your browser's
   toolbar (you may need to click the puzzle-piece icon and pin it for easy
   access).

### Signing in from the popup

1. Click the PromptShield AI icon in your toolbar.
2. Enter the same email and password you use for the admin dashboard.
3. Click **Sign in**.
4. The popup will now show your account and protection status instead of
   the login form.

You only need to do this once — the extension keeps you signed in across
browser restarts until your session naturally expires or you sign out.

### What the popup shows you

Click the toolbar icon any time to see:

- **Your signed-in account** (name/email) and a **theme toggle** (sun/moon
  icon) that switches the extension's UI between light and dark — this stays
  in sync with the dashboard's theme setting.
- **Backend connectivity status** — a live indicator of whether the
  extension can currently reach your organization's PromptShield backend.
  If this shows offline, prompts will still go through (fail open — see
  below) but won't be scanned until connectivity is restored.
- **A "Protection enabled" toggle** — this is your kill switch. Flip it off
  and the extension stops scanning entirely (prompts pass straight through
  unscanned); flip it back on to resume protection. Use this sparingly and
  intentionally.
- **Last scan** — the most recent website and decision, so you have a quick
  sanity check that things are working.
- **Sign out** — ends your session on this device.

### What happens when you type a prompt

This is the part that runs automatically, without you opening the popup at
all. It works identically on `chatgpt.com`, `chat.openai.com`, `claude.ai`,
and `gemini.google.com`:

1. You type your prompt as normal and press Enter or click Send.
2. PromptShield intercepts it *before* it reaches the AI site — the site
   never sees anything yet.
3. The prompt is sent to your organization's backend for inspection
   (typically well under a second).
4. Based on the result, one of four things happens:

   - **Nothing.** If the prompt is clean, it's sent through automatically.
     You won't see any UI at all — this is the common case for the vast
     majority of everyday prompts.
   - **A warning modal appears.** If the prompt is moderately risky, a
     custom PromptShield dialog pops up explaining what it found, with two
     buttons: **Cancel** (nothing is sent, you can edit your prompt) and
     **Continue** (sends your original prompt exactly as you wrote it).
   - **Your prompt text changes on its own, and a toast notification
     appears.** If the prompt contained clearly sensitive data
     (an email address, phone number, etc.), PromptShield replaces just
     those parts with a placeholder like `[REDACTED_EMAIL]` directly in the
     text box. **Nothing is sent automatically** — read the updated text,
     and if it still says what you need it to say, click Send again
     yourself.
   - **A block modal appears, and that's the end of it.** If the prompt
     contains something PromptShield's policies say should never be sent
     (a live API key, for example), a dialog explains why, and there's no
     "send anyway" option. The AI website never receives any version of
     that prompt.

5. If your organization's backend is temporarily unreachable (network issue,
   backend restarting), PromptShield fails open: your prompt goes through
   unscanned rather than getting stuck. This is intentional — a backend
   outage should never block your work — and it's visible in the popup's
   Backend Status indicator if you check it.

### Reading the Explainable AI panel

Every Warn and Block dialog includes a full breakdown, not just a yes/no —
this is what you'll see:

- **Overall Risk** — a score out of 100 with a severity label
  (Low/Medium/High/Critical).
- **Detected** — a checklist of specifically what was found (e.g. "AWS
  Access Key," "Internal Project Codename"), in plain language rather than
  raw detector names.
- **Triggered Policies** — which of your organization's named policies (if
  any) caused this outcome, so you know it's not arbitrary.
- **Recommended Action** — what PromptShield is doing about it.
- **Reason** — a one- or two-sentence plain-English explanation.

If something gets flagged and you don't understand why, this panel should
answer it directly without needing to ask IT — and if it's a false positive
(e.g. a keyword that happens to appear in a harmless context), that's useful
feedback for your admin to refine the relevant policy.

---

## Common Workflows, Step by Step

### Workflow: onboarding a new employee

1. Have the employee register their own account (or, as an admin, provision
   one via `seed.py`/a future admin user-creation flow) — public
   self-registration always creates a standard employee account.
2. Have them install the browser extension (see
   [Installing it in Chrome](#installing-it-in-chrome)) and sign in from the
   popup with their new credentials.
3. Check the **Employees** page in the dashboard the next day — their
   Extension status should move from "Not Installed" to "Active" once
   they've sent their first prompt.

### Workflow: writing your first policy

1. Go to **Policies** → **New Policy**.
2. Start with something safe and obvious, e.g. Name: "Block Leaked
   Credentials," Detection Type: "Any Leaked Credential (detector)," Action:
   Block, Priority: 10 (low number so it's checked early).
3. Save it, then test it yourself: open ChatGPT with the extension active
   and try a prompt containing an obviously fake API-key-shaped string.
4. Confirm in **Prompt Logs** that the scan shows up as Blocked with your
   new policy's name listed as the trigger.
5. Iterate from there — add a Warn-level policy for something less severe,
   like company keywords, and repeat the same test-and-verify cycle.

### Workflow: investigating a blocked prompt

1. An employee mentions a prompt got blocked, or you notice a spike on the
   **Dashboard**.
2. Go to **Prompt Logs**, filter Action to **Block**, and optionally search
   for the employee's name.
3. Click the relevant row to open the detail drawer.
4. Click the eye icon to reveal the original prompt (masked by default).
5. Read the **Triggered Rules** section to see exactly which detector(s)
   fired and why.
6. Decide: if it's a genuine risk, no action needed — the system did its
   job. If it's a false positive (e.g. a policy is too broad), go adjust
   that policy on the **Policies** page.

### Workflow: adding a company keyword

1. You have a new confidential project name that should never leave the
   company via an AI prompt — e.g. "Project Falcon."
2. Go to **Settings**, scroll to **Company Keywords**.
3. Type `Project Falcon` into the input and click **Add**.
4. It's live immediately — no redeploy needed. The next prompt containing
   that term (case-insensitive) will be flagged by the Company Keyword
   Detector according to whatever policy targets `company_keyword`.

### Workflow: temporarily pausing protection

Only do this when genuinely necessary (e.g. debugging why the extension
seems stuck) — it disables scanning entirely for that browser.

1. Click the PromptShield icon in the toolbar.
2. Toggle **Protection enabled** off.
3. Do whatever you needed to do.
4. Toggle it back on. Don't forget this step.

### Workflow: reviewing weekly risk trends

1. Go to **Analytics**.
2. Check **Risk Trend** for the week — is the average score climbing?
3. Check **Top Triggered Rules** — is one detector suddenly dominating
   (could mean a new risky behavior pattern, or a policy that's too
   sensitive and generating noise)?
4. Cross-reference with **Top Employees by Violations** to see if it's
   broad-based or concentrated in a few people/teams.
5. Use findings here to decide whether a policy needs tightening, loosening,
   or whether it's time for a training conversation with a specific team.

---

## Understanding the Four Decisions

| Decision | What the employee sees | What happens to the prompt |
|---|---|---|
| **ALLOW** | Nothing — completely silent | Sent through exactly as typed |
| **WARN** | A modal with Cancel/Continue | Only sent if the employee clicks Continue; sent unmodified |
| **REDACT** | The text box content changes, plus a toast | Sensitive spans replaced with placeholders like `[REDACTED_EMAIL]`; **not auto-sent** — the employee must review and click Send again |
| **BLOCK** | A modal explaining why, no way to proceed | Never sent to the AI site in any form |

---

## Troubleshooting

**The popup says "Backend offline."**
The extension can't reach your organization's PromptShield backend. Prompts
will still go through (unscanned) while this is the case. Check with your IT
admin — this usually means the backend service needs to be restarted or
there's a network issue.

**A prompt was blocked and I don't understand why.**
Open the Explainable AI panel in the block modal — it lists exactly which
finding(s) triggered it and which policy is responsible. If you believe it's
a mistake, ask your admin to check that policy on the **Policies** page in
the dashboard.

**I don't see anything happening when I type a prompt — is it working?**
That's expected for clean prompts — ALLOW is silent by design. Check the
popup's "Last scan" field to confirm a scan actually happened recently.

**I'm signed in but the dashboard says "You do not have permission."**
Some pages and all write actions (creating policies, editing settings)
require an admin or security_analyst role. If you're a regular employee
account, you won't have dashboard access at all — the dashboard is a
security-team tool, not an employee-facing surface.

**My session keeps logging out.**
Access tokens expire after 60 minutes by default (configurable by your
admin via `ACCESS_TOKEN_EXPIRE_MINUTES`). Just sign in again — there's no
data loss.

---

## Demo Credentials Reference

If you're evaluating a fresh local setup seeded with `python seed.py`, these
accounts already exist:

| Role | Email | Password |
|---|---|---|
| Admin (full dashboard access) | `admin@promptshield.ai` | `Admin@12345` |
| Sample employee | `priya.sharma@acme.com` | `Employee@12345` |

The seed also creates 20 employees across 10 departments and ~260 sample
scan log entries spread across the last 30 days, so every page in this guide
will already have realistic data to look at on first login — nothing you see
in a fresh seeded environment is fake or placeholder data, it's exactly the
same code path real usage would produce.
