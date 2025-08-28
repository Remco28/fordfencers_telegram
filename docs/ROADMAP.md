# Family Organizer Telegram Bot – Roadmap

## Vision
- Simple, reliable family group bot for to-dos, tournaments, and reminders.
- Clean inline-menu UX, low maintenance, safe-by-default.

## Guiding Principles
- Keep scope small; ship incremental slices.
- Prefer correctness and resilience over features.
- Store UTC in DB; present in local timezone.
- Use parameterized SQL; avoid global DB state in async.
- Use PTB JobQueue for scheduling (not APS in MVP).

## Milestones & Phases

### Phase 0 – Foundations (this cycle)
- Decide architecture, schema, and handler layout.
- Bootstrap minimal test bot on GCE with `/start`, `/health`.
- Journald logging; systemd service with auto-restart.

### Phase 1 – To-Dos MVP
- DB: `todos` table (+ WAL, indexes).
- Views: All, by kid, overdue.
- Actions: Add, Done, Reschedule (Today/Tomorrow/Date).
- Daily overdue digest via JobQueue.

### Phase 2 – Reminders & Tournaments
- One-off reminders (per-message scheduling).
- Tournaments list/add with date.
- Basic export (text dump) for safety.

### Phase 3 – Polish & Ops
- Access control (allowed chat IDs).
- Timezone config; friendly date parsing.
- Error handling, monitoring, and backup routine.

## Workstreams
- Application: Handlers, keyboards, callback protocol.
- Data: SQLite init, CRUD, migrations, backups.
- Scheduling: JobQueue wrappers and daily jobs.
- DevEx: Config, logging, deployment, docs.

## Initial Task Breakdown
- Bootstrap test bot (see spec in `comms/tasks/`).
- Establish config module and env vars.
- Add health/version commands and logging.
- Prepare DB module (init only; no CRUD yet).
- Wire JobQueue and daily no-op job (smoke test).

## Risks & Mitigations
- SQLite concurrency: per-operation connections + WAL.
- Group privacy mode: rely on commands and callbacks; entity parsing for mentions later.
- Callback size limits: compact callback_data encoding.
- Timezones: store UTC; configurable local TZ for display/jobs.

## Definition of Done (per phase)
- All acceptance criteria for the phase met.
- Deployed on GCE, service active, basic manual test passes.
- Notes captured in `comms/log.md`; spec archived when approved.

