# PromptShield AI

**The AI firewall for teams using ChatGPT, Claude & Gemini.**

PromptShield AI is an enterprise-grade AI firewall made of three parts that
work together: a Chrome extension that inspects every prompt an employee
sends to a public AI tool, a FastAPI backend with a nine-stage detection
pipeline that decides what happens to that prompt, and a React admin
dashboard where security teams configure policy and watch it all happen
live. It was built as a hackathon MVP — no placeholders, no mock data,
every screen backed by a real MySQL database.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Screenshots](#screenshots)
6. [Installation](#installation)
7. [Running the Backend](#running-the-backend)
8. [Running the Admin Dashboard](#running-the-admin-dashboard)
9. [Loading the Browser Extension](#loading-the-browser-extension)
10. [Creating the MySQL Database](#creating-the-mysql-database)
11. [Environment Variables](#environment-variables)
12. [Demo Credentials](#demo-credentials)
13. [Project Structure](#project-structure)
14. [Known Limitations](#known-limitations)
15. [Production Hardening (Milestone 6)](#production-hardening-milestone-6)
16. [Manual Test Checklist](#manual-test-checklist)
17. [Future Scope](#future-scope)

---

## Project Overview

Employees don't stop using ChatGPT, Claude, or Gemini just because IT asks
them to. PromptShield AI accepts that reality and puts a firewall in the
one place that matters: the moment a prompt is about to leave the browser.

- **Browser Extension** — a Manifest V3 extension that sits quietly inside
  `chatgpt.com`, `chat.openai.com`, `claude.ai`, and `gemini.google.com`.
  It intercepts the prompt textbox on submit, sends the text (and any
  attached files) to the backend, and enforces whatever decision comes
  back — before the AI site ever sees the original text.
- **FastAPI Backend** — a single `POST /api/scan` endpoint runs every
  prompt through a nine-stage detection pipeline (normalizer → regex →
  Presidio → spaCy → source-code detector → company keyword matcher →
  detect-secrets → file scanner → policy engine → risk engine → decision
  engine → redactor), logs the result to MySQL, and returns one of four
  decisions: **ALLOW**, **WARN**, **REDACT**, or **BLOCK**.
- **Admin Dashboard** — a React console where security teams see every
  scanned prompt, author detection policies, track employee risk, and
  read analytics — all computed live from the same `audit_logs` table the
  extension writes to.

No Redis, no Kafka, no Docker, no Kubernetes, no Elasticsearch. Just
FastAPI, MySQL, and two Vite-built frontends.

## Features

**Detection Engine**
- Regex detection for emails, phone numbers, URLs, AWS/GitHub/OpenAI keys, JWTs, and more.
- Microsoft Presidio for PII (names, locations, credit cards, and other entities).
- spaCy NER as a second-opinion entity detector.
- `detect-secrets` for live credentials (API keys, private keys, tokens) using a curated,
  deterministic plugin set — entropy-based plugins are deliberately excluded (see
  [Known Limitations](#known-limitations)).
- Source-code detector (flags Python/JavaScript/SQL/etc. pasted into a prompt).
- Company keyword matcher against an admin-configurable keyword list.
- File scanner for PDFs, Word docs, spreadsheets, images (OCR), and YAML/config files.
- A policy engine that maps any detection category to `ALLOW` / `WARN` / `REDACT` / `BLOCK`,
  evaluated in admin-defined priority order.
- A risk engine that aggregates every detector's findings into one risk score and severity.

**Browser Extension**
- Custom React UI rendered inside a closed Shadow DOM — no `alert()`/`confirm()`, ever.
- An **Explainable AI panel** on every WARN/BLOCK: overall risk score, each individual
  finding, the policy that fired, the recommended action, and a plain-language reason.
- WARN shows a modal with Cancel/Continue. REDACT rewrites the prompt in place and requires
  the employee to manually re-send (no silent auto-resubmit). BLOCK stops submission outright.
- Hardened site adapters with multiple selector fallback strategies, MutationObserver +
  polling + SPA-navigation detection so it keeps working as ChatGPT/Claude/Gemini update
  their DOM.
- Popup shows signed-in user, derived organization, live backend connectivity, a
  protection on/off switch, and the last scan result.

**Admin Dashboard**
- **Dashboard** — security score, prompt/violation counters, daily activity chart, risk
  distribution, top violation types, website usage, and a live recent-activity feed.
- **Prompt Logs** — searchable, filterable, paginated table with a detail drawer showing
  both the original and sanitized prompt, every detector finding, and the triggered policy.
- **Policies** — full CRUD with priority ordering, detection-type mapping, and an
  enable/disable toggle.
- **Employees** — directory with department, role, prompt volume, violation count, and a
  live "last active" / "extension status" computed from real scan activity.
- **Analytics** — risk trends, department breakdowns, and website usage over time.
- **Settings** — organization name, risk threshold, supported websites, and the company
  keyword list, all persisted to MySQL.

## Architecture

```
  Browser Extension (Manifest V3)          Admin Dashboard (React + Vite)
  ChatGPT / Claude / Gemini adapters       Live security console
            |                                          |
            |  POST /api/scan                          |  /api/dashboard, /api/prompt-logs,
            |  <- ALLOW / WARN / REDACT / BLOCK         |  /api/policies, /api/employees, ...
            v                                          v
  +---------------------------------------------------------------+
  |                        FastAPI Backend                        |
  |  Normalizer -> Regex -> Presidio -> spaCy -> Source Code ->    |
  |  Company Keyword -> detect-secrets -> File Scanner ->          |
  |  Policy Engine -> Risk Engine -> Decision Engine -> Redactor -> |
  |  Audit Logger                                                  |
  +--------------------------------|--------------------------------+
                                    v
                        +-----------------------+
                        |       MySQL 8.4        |
                        |  users, audit_logs,     |
                        |  policies,               |
                        |  company_keywords,        |
                        |  org_settings               |
                        +-----------------------+
```

Every detector returns the same `DetectionResult` shape (`detector`,
`severity`, `score`, `matches`, `recommendation`, `reason`), so the risk
engine can aggregate across all nine stages without special-casing any one
of them. See `docs/SYSTEM_ARCHITECTURE.md` and `docs/API_DOCUMENTATION.md`
for the full breakdown.

## Tech Stack

| Component | Stack |
|---|---|
| Backend | FastAPI 0.115, SQLAlchemy 2.0, Pydantic v2, PyMySQL, python-jose (JWT), Passlib+bcrypt |
| Detection Engine | spaCy, Presidio Analyzer/Anonymizer, detect-secrets, langdetect, pypdf, python-docx, openpyxl, pytesseract |
| Database | MySQL 8.4 (no Alembic — `Base.metadata.create_all()` on startup) |
| Admin Dashboard | React 19, Vite, TypeScript, Tailwind CSS v4, TanStack Query, Recharts, Framer Motion, React Router |
| Browser Extension | Manifest V3, React 19, Vite, TypeScript, Tailwind CSS v4 |

## Screenshots

_Add screenshots of the running dashboard and extension here before sharing this README:_

- `docs/screenshots/dashboard.png` — Dashboard overview
- `docs/screenshots/prompt-logs.png` — Prompt Logs table + detail drawer
- `docs/screenshots/policies.png` — Policy editor
- `docs/screenshots/extension-warn.png` — Extension WARN modal with Explainable AI panel
- `docs/screenshots/extension-block.png` — Extension BLOCK modal

## Installation

**Prerequisites**

- Python 3.10+
- Node.js 20+
- MySQL 8.4 (running locally or reachable over the network)
- Google Chrome (or any Chromium-based browser) for the extension

Clone the repository, then set up each of the three components as described below.

## Running the Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional but recommended - improves PII/NER detection accuracy:
python -m spacy download en_core_web_sm

cp .env.example .env             # then edit .env - see Environment Variables below
python seed.py                   # creates the admin user, demo org, and ~260 sample logs
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`. Interactive docs are at
`http://localhost:8000/docs`.

## Running the Admin Dashboard

```bash
cd admin-dashboard
npm install
npm run dev
```

Open `http://localhost:5173`. Sign in with the [demo credentials](#demo-credentials)
below, or visit `/` for the marketing landing page.

## Loading the Browser Extension

```bash
cd browser-extension
npm install
npm run build
```

Then in Chrome:

1. Go to `chrome://extensions`.
2. Turn on **Developer mode** (top right).
3. Click **Load unpacked** and select `browser-extension/dist`.
4. Open the extension popup and sign in with the same credentials as the dashboard.
5. Visit `chatgpt.com`, `claude.ai`, or `gemini.google.com` and send a prompt — PromptShield
   will scan it before it reaches the site.

## Creating the MySQL Database

```sql
CREATE DATABASE promptshield CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'promptshield'@'localhost' IDENTIFIED BY 'change-this-password';
GRANT ALL PRIVILEGES ON promptshield.* TO 'promptshield'@'localhost';
FLUSH PRIVILEGES;
```

Point `backend/.env` at this database (see below) and run `python seed.py` — the backend
creates every table automatically on first run via SQLAlchemy's metadata, no migration
tool required.

## Environment Variables

`backend/.env` (copy from `backend/.env.example`):

| Variable | Description | Example |
|---|---|---|
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_NAME` | Database name | `promptshield` |
| `DB_USER` | Database user | `root` |
| `DB_PASSWORD` | Database password | `changeme` |
| `JWT_SECRET_KEY` | Secret used to sign access tokens — **change this in production** | a long random string |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Reserved for a future refresh-token endpoint | `7` |
| `ENVIRONMENT` | `development` or `production` | `development` |
| `CORS_ORIGINS` | Comma-separated list of allowed origins (dashboard + extension) | `http://localhost:5173,chrome-extension://*` |
| `OPENROUTER_API_KEY` | Optional — enables the semantic classifier detector | _(blank disables it gracefully)_ |

## Demo Credentials

Running `python seed.py` creates a demo organization with:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@promptshield.ai` | `Admin@12345` |
| Any seeded employee (e.g. Priya Sharma) | `priya.sharma@acme.com` | `Employee@12345` |

The seed also creates 20 employees across 10 departments, 5 default policies, 5 company
keywords, and ~260 realistic prompt-scan log entries spread across the last 30 days, so the
dashboard looks alive immediately.

## Project Structure

```
firewall appln/
├── backend/
│   ├── ai/                  # Detection engine: normalizer, 8 detectors, risk/policy/decision engines, redactor, pipeline
│   ├── auth/                 # Password hashing, JWT issuing, dependencies (require_admin, etc.)
│   ├── config/                # Pydantic settings
│   ├── middleware/             # Request logging
│   ├── models/                  # SQLAlchemy models (User, Policy, CompanyKeyword, AuditLog, OrgSettings)
│   ├── routers/                  # auth, health, scan, dashboard, analytics, prompt_logs, policies, employees, settings
│   ├── schemas/                    # Pydantic request/response schemas
│   ├── services/                    # Business logic shared by routers (analytics, employees, settings, audit, policy)
│   ├── seed.py                       # Demo data seeder (idempotent)
│   ├── main.py                        # FastAPI app entrypoint
│   └── requirements.txt
├── admin-dashboard/
│   └── src/
│       ├── components/        # Shared UI (Button, Card, Drawer, Pagination, EmptyState, ErrorState, Logo, ...)
│       ├── context/             # Auth + Theme providers
│       ├── lib/                   # adminApi.ts (typed API client), format.ts
│       ├── pages/                   # LandingPage, LoginPage, Dashboard/PromptLogs/Policies/Employees/Analytics/Settings, NotFoundPage
│       └── types/                     # TS mirrors of backend Pydantic schemas
├── browser-extension/
│   ├── public/                # manifest.json, icons/
│   ├── scripts/                 # generate_icons.py (regenerates toolbar icons from the brand mark)
│   └── src/
│       ├── adapters/              # Per-site DOM adapters (ChatGPT, Claude, Gemini)
│       ├── background/              # Service worker: JWT expiry, health polling, protection toggle
│       ├── content/                   # Content script + React UI (modals, toast, Explainable AI panel)
│       ├── popup/                       # Extension popup UI
│       ├── services/                      # api.ts, theme.ts
│       └── utils/                           # dom.ts, jwt.ts, labels.ts, org.ts
└── docs/                          # SYSTEM_ARCHITECTURE.md, DATABASE_SCHEMA.md, API_DOCUMENTATION.md,
                                    # EXTENSION_ARCHITECTURE.md, BUSINESS_MODEL.md, PROJECT_STRUCTURE.md
```

## Known Limitations

- **spaCy / Presidio NER model**: `en_core_web_sm` could not be downloaded in the sandbox
  this project was built in (its GitHub release host was blocked by the sandbox's network
  proxy). Both detectors degrade gracefully to a neutral no-op result when the model is
  missing rather than crashing — run `python -m spacy download en_core_web_sm` on your own
  machine to enable full PII/NER detection.
- **`detect-secrets` entropy plugins are intentionally disabled**: testing showed
  Base64/Hex high-entropy plugins flag ordinary English words (e.g. "banana") as secrets.
  The secret detector uses a curated set of 24 deterministic, pattern-based plugins instead
  (AWS keys, GitHub/GitLab tokens, private keys, Slack/Stripe/Twilio tokens, and more).
- **No refresh-token endpoint**: the extension detects JWT expiry client-side (decoding the
  token payload) and prompts a clean re-login rather than silently refreshing, since the
  backend intentionally does not implement token refresh in this MVP.
- **Semantic classifier is optional**: the OpenRouter-based semantic classifier only runs
  if `OPENROUTER_API_KEY` is set; without it, the other eight detection stages still run
  normally.
- **Single-tenant demo data**: the seeded "Demo Organization" data is for local evaluation
  only — there is no multi-tenant isolation in this MVP (see [Future Scope](#future-scope)).
- **JWT stored in `chrome.storage.local`**: this is plaintext, on-disk storage - the only
  practical option for a Manifest V3 extension without a native messaging host. Reviewed as
  part of Milestone 6's security pass and accepted as a platform constraint rather than a
  fixable bug; a shorter access-token lifetime is the main lever available without a bigger
  architecture change.
- **Rate limiting is in-memory, single-instance**: `POST /api/auth/login` and `/register`
  are throttled per-IP (10 attempts/minute) to blunt brute-force attempts, but the limiter's
  state lives in the FastAPI process's memory - a multi-instance production deployment
  behind a load balancer would need this backed by a shared store (Redis) instead, which is
  out of scope for this MVP's "no Redis" constraint.
- **Uncaught 500s have no external alerting**: FastAPI's default exception handling never
  leaks stack traces to the client, and unhandled exceptions are now logged with full
  tracebacks (see `middleware/logging.py`), but there's no Sentry/observability integration
  in this MVP - a real deployment would want one.

## Production Hardening (Milestone 6)

After Milestones 1-5 shipped a feature-complete hackathon MVP, a full staff-engineer-level
review of the codebase (backend, dashboard, extension, database, security, accessibility)
found and fixed several real issues rather than adding new features:

- Closed a **critical privilege-escalation bug**: `POST /api/auth/register` used to accept
  a client-supplied `role` field, letting anyone self-register as an admin. Public
  registration now always creates a plain employee account.
- Added **fault isolation** to the detection pipeline so one detector's unexpected exception
  degrades to a neutral result instead of crashing the whole scan (and losing the audit log
  entry for a legitimate prompt).
- Added **file-upload size/count limits** on `/api/scan` (max 5 files, ~10MB each) to close
  a memory-exhaustion DoS vector.
- Fixed the extension's `scanPrompt()` **silently failing open on an expired session** (401)
  exactly the same as a healthy "nothing to flag" response - it now clears the stale session
  so the employee is prompted to re-authenticate instead of unknowingly running unprotected.
- Fixed `User.extension_status` being **permanently stale** on `/api/auth/me` (always
  `not_installed`) while `/api/employees` computed it correctly - both now compute it live.
- Added **indexes** on `audit_logs.website/action/risk` (see `docs/DATABASE_SCHEMA.md`) and
  **rate limiting** on the login/register endpoints.
- **Debounced** the Prompt Logs and Employees search inputs (were firing a network request
  on every keystroke).
- Gave the Drawer, ConfirmDialog, and PolicyFormModal components consistent **keyboard
  navigation and screen-reader semantics** (`role`/`aria-*`, focus trapping, Escape-to-close,
  focus restored on close) via one shared `useDialogA11y` hook, instead of each
  reimplementing a different partial subset.
- Removed a **duplicated `SEVERITY_RANK` dict** that was copy-pasted into five detector
  files, extracting it into `schemas/detection.py` once.

## Manual Test Checklist

Automated tests cover the API end-to-end (SQLite-backed FastAPI `TestClient` runs), but the
extension's real-world DOM behavior should be spot-checked by hand after any change:

- [ ] On `chatgpt.com`: send a benign prompt → **ALLOW**, prompt goes through unmodified.
- [ ] On `chatgpt.com`: send a prompt containing a company keyword → **WARN** modal appears
      with Cancel/Continue; Continue re-sends the original text.
- [ ] On `claude.ai`: send a prompt with an email + phone number → **REDACT** rewrites the
      textbox; prompt is *not* auto-sent — you must click Send yourself.
- [ ] On `gemini.google.com`: send a prompt with a fake AWS key → **BLOCK** modal appears;
      confirm the network tab shows the request never reached the AI site's own backend.
- [ ] Every WARN/BLOCK modal shows the Explainable AI panel (risk score, findings, triggered
      policy, recommended action, reason) — not a generic error.
- [ ] Reload the extension mid-conversation and confirm the content script reconnects
      without a full page refresh.
- [ ] Toggle protection off in the popup and confirm prompts pass through unscanned; toggle
      it back on.
- [ ] Switch the dashboard/extension theme and confirm both stay in sync via
      `chrome.storage`.

## Future Scope

- Multi-tenant organizations with SSO/SAML.
- A refresh-token endpoint and silent session renewal.
- Firefox/Edge extension builds, plus adapters for Gmail, Outlook, Teams, and Slack.
- SIEM export (Splunk/Datadog) and webhook alerting on BLOCK events.
- Fine-grained per-department policy overrides.
- A managed cloud offering alongside the self-hosted deployment described in this README.

See `docs/BUSINESS_MODEL.md` for the full roadmap and go-to-market plan.

---

© 2026 PromptShield AI. Built as a hackathon MVP for enterprise AI governance.
