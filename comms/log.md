<!-- Example log -->
[2025-08-26 09:00] [Gemini]: SETUP: Initialized comms directory structure and logging protocol.

<!-- example log -->
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
[2025-08-27 23:06] [Frank]: Google Cloud VM server acquired. Set up in progress.
[2025-08-28 14:30] [CLAUDE]: IMPL IN_PROGRESS: Phase 1 Asks MVP implementation
[2025-08-28 14:45] [CLAUDE]: IMPL DONE: Phase 1 Asks MVP - full multi-assignee Ask system with DM-based flows, SQLite database, conversation handlers, and all specified features
[2025-08-28 15:00] [CLAUDE]: IMPL IN_PROGRESS: Applying bug fixes and improvements per architect review notes
[2025-08-28 15:05] [CLAUDE]: IMPL DONE: Critical bug fix - /ask DM command now works without async errors, plus version consistency and deterministic chat ID selection
[2025-08-28 15:10] [CLAUDE]: IMPL IN_PROGRESS: Fixing context user data key consistency - aligning with spec pseudocode
[2025-08-28 15:12] [CLAUDE]: IMPL DONE: Context user data key consistency fix - changed 'selected_assignees' to 'sel' to match spec pseudocode
[2025-08-28 15:20] [Architect]: SPEC READY: Mini App MVP spec added at comms/tasks/2025-08-28-mini-app-mvp.md and ROADMAP updated for Mini App phases.
[2025-08-28 15:22] [Architect]: DOC ADDED: Introduced TECHADVISOR.md to define the Technical Advisor role, scope, workflow, and deliverables.
[2025-08-28 15:28] [Architect]: DOC UPDATED: Revised TECHADVISOR.md for a lightweight, non-corporate workflow and tone.
[2025-08-28 15:35] [Architect]: SPEC READY: Tech Debt Quick Fixes — branding unification, PRIMARY_CHAT_ID, ask aggregation refactor, DM self-assign guard; see comms/tasks/2025-08-28-tech-debt-quick-fixes.md.
[2025-08-28 15:35] [Architect]: DOC UPDATED: ROADMAP now notes transition to DigitalOcean (domain/DNS/hosting); GCP docs retained temporarily for reference.
[2025-08-28 15:45] [Architect]: DOC ADDED: DigitalOcean setup guide at docs/digitalocean-setup.md (Droplet, DNS, Caddy HTTPS, systemd services).
[2025-08-28 15:45] [Architect]: BRANCH CREATED: feature/mini-app-mvp for Mini App and related changes.
[2025-08-28 15:52] [Architect]: DOC ADDED: Git Branching Cheatsheet at docs/git-branching-cheatsheet.md (commands, tips for local/server, branch juggling).
\n+[2025-08-28 15:31] [TECHADVISOR]: ADVISORY NOTES: Ford-Fencers Telegram – Asks MVP state + Mini App prep
- Good: DM-first Asks flows complete; unified /ask DM entry; SQLite WAL + indexes; deterministic chat_id via next(iter(ALLOWED_CHAT_IDS)); graceful DM notification failures handled.
- Risk (med): Bot naming inconsistency ("UsualSuspects" vs "Ford-Fencers-Bot"). Why it matters: user trust + onboarding clarity. Mitigation: standardize strings in handlers/commands.py and docs to the official handle.
- Risk (low): GROUP_CONCAT parsing in db.get_all_open_asks fragile for names with commas. Mitigation: aggregate in Python instead of splitting concatenated strings.
- Risk (low): Mini App config missing. Mitigation: add WEBAPP_URL and stub FastAPI service + static webapp per spec.
- Do now: unify branding strings; refactor get_all_open_asks to Python grouping; add WEBAPP_URL and deps (fastapi, uvicorn[standard], itsdangerous, python-multipart); create web_server.py skeleton and webapp/ scaffold.
- Next: optional PRIMARY_CHAT_ID env; add welcome DM button when WEBAPP_URL set; keep INFO logs consistent (user_id, chat_id) across handlers.
- Questions: confirm official bot username/handle; allow self-assign in New Ask or exclude requester; confirm hosting/HTTPS target for WEBAPP_URL.
