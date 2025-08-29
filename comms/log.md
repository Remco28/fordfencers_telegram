[2025-08-26 09:00] [Gemini]: SETUP: Initialized comms directory structure and logging protocol.
[2025-08-27 23:06] [Frank]: Google Cloud VM server acquired. Set up in progress.
[2025-08-28 01:36] [Architect]: SPEC READY: Added docs/ROADMAP.md and task spec at comms/tasks/2025-08-28-test-bot-bootstrap.md.
[2025-08-28 01:38] [Architect]: DOC ADDED: Step-by-step GCE VM setup guide at docs/gce-vm-setup.md.
[2025-08-28 03:08] [Developer]: IMPL DONE: Minimal test bot implemented (commands, config, keyboards).
[2025-08-28 03:08] [Architect]: REVIEW PASS: Implementation matches spec; archiving task to comms/tasks/archive/.
[2025-08-28 04:34] [Architect]: SPEC READY: Phase 1 Asks MVP spec added at comms/tasks/2025-08-28-asks-mvp.md.
[2025-08-28 04:36] [Architect]: DOC UPDATED: ROADMAP.md updated to reflect Asks MVP focus and phases.
[2025-08-28 04:49] [Architect]: REVIEW NOTES: Posted Asks MVP change notes at comms/tasks/2025-08-28-asks-mvp-review-notes.md for dev feedback.
[2025-08-28 05:00] [Architect]: SPEC UPDATED: Amended Asks MVP spec to require unified /ask DM entry and added implementation notes.
[2025-08-28 05:03] [Architect]: REVIEW PASS: Verified /ask DM entry fix, deterministic chat_id, and version sourcing; ready to deploy and test.
[2025-08-28 05:10] [Architect]: CODE UPDATED: Renamed bot strings to Ford-Fencers-Bot, adjusted group prompts to @Ford-Fencers-Bot, updated group menu to [Asks, Tournaments], ensured DM /start shows DM menu.
[2025-08-28 05:10] [Architect]: DOC UPDATED: Renamed roadmap and GCE setup guide to Ford-Fencers-Bot; updated service/unit examples and commands.
[2025-08-28 14:20] [CLAUDE]: IMPL IN_PROGRESS: Bootstrap minimal test bot implementation
[2025-08-28 14:25] [CLAUDE]: IMPL DONE: Bootstrap minimal test bot - created requirements.txt, config.py, handlers/commands.py, keyboards.py, app.py with /start, /health, /version commands
[2025-08-28 14:30] [CLAUDE]: IMPL IN_PROGRESS: Phase 1 Asks MVP implementation
[2025-08-28 14:45] [CLAUDE]: IMPL DONE: Phase 1 Asks MVP - full multi-assignee Ask system with DM-based flows, SQLite database, conversation handlers, and all specified features
[2025-08-28 15:00] [CLAUDE]: IMPL IN_PROGRESS: Applying bug fixes and improvements per architect review notes
[2025-08-28 15:05] [CLAUDE]: IMPL DONE: Critical bug fix - /ask DM command now works without async errors, plus version consistency and deterministic chat ID selection
[2025-08-28 15:10] [CLAUDE]: IMPL IN_PROGRESS: Fixing context user data key consistency - aligning with spec pseudocode
[2025-08-28 15:12] [CLAUDE]: IMPL DONE: Context user data key consistency fix - changed 'selected_assignees' to 'sel' to match spec pseudocode
[2025-08-28 15:20] [Architect]: SPEC READY: Mini App MVP spec added at comms/tasks/2025-08-28-mini-app-mvp.md and ROADMAP updated for Mini App phases.
[2025-08-28 15:22] [Architect]: DOC ADDED: Introduced TECHADVISOR.md to define the Technical Advisor role, scope, workflow, and deliverables.
[2025-08-28 15:28] [Architect]: DOC UPDATED: Revised TECHADVISOR.md for a lightweight, non-corporate workflow and tone.
[2025-08-28 15:31] [TECHADVISOR]: ADVISORY NOTES: Ford-Fencers Telegram – Asks MVP state + Mini App prep
- Good: DM-first Asks flows complete; unified /ask DM entry; SQLite WAL + indexes; deterministic chat_id via next(iter(ALLOWED_CHAT_IDS)); graceful DM notification failures handled.
- Risk (med): Bot naming inconsistency ("UsualSuspects" vs "Ford-Fencers-Bot"). Why it matters: user trust + onboarding clarity. Mitigation: standardize strings in handlers/commands.py and docs to the official handle.
- Risk (low): GROUP_CONCAT parsing in db.get_all_open_asks fragile for names with commas. Mitigation: aggregate in Python instead of splitting concatenated strings.
- Risk (low): Mini App config missing. Mitigation: add WEBAPP_URL and stub FastAPI service + static webapp per spec.
- Do now: unify branding strings; refactor get_all_open_asks to Python grouping; add WEBAPP_URL and deps (fastapi, uvicorn[standard], itsdangerous, python-multipart); create web_server.py skeleton and webapp/ scaffold.
- Next: optional PRIMARY_CHAT_ID env; add welcome DM button when WEBAPP_URL set; keep INFO logs consistent (user_id, chat_id) across handlers.
- Questions: confirm official bot username/handle; allow self-assign in New Ask or exclude requester; confirm hosting/HTTPS target for WEBAPP_URL.
[2025-08-28 15:35] [Architect]: SPEC READY: Tech Debt Quick Fixes — branding unification, PRIMARY_CHAT_ID, ask aggregation refactor, DM self-assign guard; see comms/tasks/2025-08-28-tech-debt-quick-fixes.md.
[2025-08-28 15:35] [Architect]: DOC UPDATED: ROADMAP now notes transition to DigitalOcean (domain/DNS/hosting); GCP docs retained temporarily for reference.
[2025-08-28 15:45] [Architect]: DOC ADDED: DigitalOcean setup guide at docs/digitalocean-setup.md (Droplet, DNS, Caddy HTTPS, systemd services).
[2025-08-28 15:45] [Architect]: BRANCH CREATED: feature/mini-app-mvp for Mini App and related changes.
[2025-08-28 15:52] [Architect]: DOC ADDED: Git Branching Cheatsheet at docs/git-branching-cheatsheet.md (commands, tips for local/server, branch juggling).
[2025-08-28 15:53] [CLAUDE]: IMPL IN_PROGRESS: Tech Debt Quick Fixes - branding unification, PRIMARY_CHAT_ID implementation, ask aggregation refactor, self-assign prevention
[2025-08-28 16:05] [CLAUDE]: IMPL DONE: Tech Debt Quick Fixes completed - unified branding with configurable BOT_DISPLAY_NAME/BOT_HANDLE, deterministic PRIMARY_CHAT_ID chat selection, Python-based ask aggregation (no GROUP_CONCAT), self-assign prevention in DM flow, and consistent logging format
[2025-08-28 16:22] [Architect]: SPEC READY: Bot branding unification — display name Ford-Fencers-Bot, handle @UsualSuspects_bot; see comms/tasks/2025-08-28-bot-branding-unification.md.
[2025-08-28 16:25] [CLAUDE]: IMPL IN_PROGRESS: Bot branding unification - updating defaults, validation, startup logging, and documentation
[2025-08-28 16:35] [CLAUDE]: IMPL DONE: Bot branding unification completed - config defaults updated (Ford-Fencers-Bot/@UsualSuspects_bot), BOT_HANDLE validation with normalization and logging, startup banner uses settings, all documentation updated with consistent branding
[2025-08-28 16:40] [Architect]: SPEC READY: Mini App — Slice 1 (Auth + API + DM Entry) prepared at comms/tasks/2025-08-28-mini-app-slice-1-auth-and-endpoints.md.
[2025-08-28 22:55] [Architect]: REVIEW PASS: Tech Debt Quick Fixes meet spec (branding, PRIMARY_CHAT_ID, Python grouping, self-assign guard, logging consistency).
[2025-08-28 23:05] [Architect]: REVIEW PASS: Bot branding unification matches spec; defaults + validation + docs consistent.
[2025-08-28 23:15] [Architect]: LOG MAINTENANCE STARTED: Cleaned formatting artifacts and chronological order in comms/log.md.
[2025-08-28 23:15] [Architect]: LOG MAINTENANCE DONE: Verified entries and normalized spacing.
[2025-08-28 23:18] [Architect]: REVIEW NOTES: Mini App MVP partial — APIs/auth present; gaps: no static serving at /miniapp, no DM notifications on API create_ask, no /set_menu admin to set Menu Button; opened follow-up spec.
[2025-08-28 23:18] [Architect]: SPEC READY: Mini App MVP — Review Fixes at comms/tasks/2025-08-28-mini-app-mvp-review-fixes.md.
[2025-08-28 23:35] [Architect]: SPEC UPDATED: Mini App Review Fixes now require ADMIN_USER_ID(S) for /set_menu gating; added to config section.
[2025-08-28 23:16] [CLAUDE]: IMPL IN_PROGRESS: Mini App Slice 1 - implementing auth, API endpoints, and DM WebApp entry
[2025-08-28 23:18] [CLAUDE]: IMPL DONE: Mini App Slice 1 complete - FastAPI backend with Telegram WebApp auth, authenticated APIs (/api/me, /api/roster, /api/assignments/my, /api/asks), minimal frontend webapp/index.html, and DM WebApp button integration
[2025-08-28 23:33] [TECHADVISOR]: ADVISORY NOTES: Mini App pivot check — static mount at /miniapp, API-side DM notifications, and `/set_menu` admin setup are pending. Recommend: mount `webapp/` via StaticFiles(html=true) with index fallback; DM assignees from `/api/asks` (ignore BadRequest/Forbidden); add DM-only `/set_menu` guarded by `ADMIN_USER_ID`; optionally introduce `SESSION_SECRET` and set basic CSP at proxy. Questions: confirm bot handle and `WEBAPP_URL` domain; number of admins.
[2025-08-28 23:35] [CLAUDE]: IMPL IN_PROGRESS: Mini App MVP Review Fixes - static serving, API DM notifications, assignee picker fixes, and admin /set_menu command
[2025-08-28 23:40] [CLAUDE]: IMPL DONE: Mini App MVP Review Fixes completed - added ADMIN_USER_IDS config, static /miniapp/ serving, DM notifications in API create_ask, fixed assignee picker to exclude requester, and added admin-only /set_menu command with MenuButtonWebApp
[2025-08-28 23:46] [Architect]: SPEC READY: Mini App SPA fallback + small polish at comms/tasks/2025-08-28-mini-app-spa-fallback-and-polish.md.
[2025-08-28 23:47] [CLAUDE]: IMPL IN_PROGRESS: Mini App SPA fallback and polish - implementing SPA routing fallback, typing polish, and optional dev CORS
[2025-08-28 23:50] [CLAUDE]: IMPL DONE: Mini App SPA fallback and polish completed - replaced StaticFiles mount with explicit SPA fallback routing (/miniapp/{path:path} returns index.html), fixed typing (any → Any), added optional dev CORS with ENABLE_DEV_CORS env flag, removed unused StaticFiles import
[2025-08-28 20:05] [Architect]: ARCHIVE: Moved comms/tasks/2025-08-28-asks-mvp.md to comms/tasks/archive/.
[2025-08-28 20:05] [Architect]: ARCHIVE: Moved comms/tasks/2025-08-28-asks-mvp-review-notes.md to comms/tasks/archive/.
[2025-08-28 20:05] [Architect]: ARCHIVE: Moved comms/tasks/2025-08-28-tech-debt-quick-fixes.md to comms/tasks/archive/.
[2025-08-28 20:05] [Architect]: ARCHIVE: Moved comms/tasks/2025-08-28-bot-branding-unification.md to comms/tasks/archive/.
[2025-08-28 20:18] [Architect]: DOC UPDATED: ARCHITECTURE.md augmented with runtime, concurrency, security, observability, and schema notes; fixed DB filename reference.
