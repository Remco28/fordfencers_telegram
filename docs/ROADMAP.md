# Ford-Fencers-Bot – Roadmap

## Vision
- Simple, reliable family bot focused on lightweight “Asks” (ask <person> to do <thing>), with future tournaments and reminders.
- Clean DM-first UX to keep the group chat tidy; low maintenance, safe-by-default.

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

### Phase 1 – Asks MVP (current)
- DM flows for creating an Ask, selecting multiple assignees, and submitting text.
- “My Asks” list for each user with Done (with confirmation) and requester DM notification on completion.
- “All Open Asks” compact DM summary.
- SQLite schema: `users`, `asks`, `ask_assignees`; WAL + indexes.

### Phase 2 – Tournaments & Reminders
- Tournaments: list/add simple dated events (optional, low volume).
- Reminders: one-off notifications (via PTB JobQueue) for selected items.
- Basic export (text dump) for safety.

### Phase 3 – Polish & Ops
- Access control (allowed chat IDs).
- Timezone config; friendly date parsing.
- Error handling, monitoring, and backup routine.

## Workstreams
- Application: Handlers, keyboards, compact callback protocol (`ak:*`).
- Data: SQLite init, CRUD, WAL, backups plan.
- Scheduling (later): JobQueue wrappers for reminders.
- DevEx: Config, logging, deployment, docs.

## Initial Task Breakdown
- Bootstrap test bot (done; archived spec).
- Phase 1 spec for Asks MVP (done; see `comms/tasks/`).
- Implement DB module and handlers per spec (create/list/done/notify).
- DM-first menus and roster registration on DM `/start`.
- Light error handling and INFO logging.

## Risks & Mitigations
- SQLite concurrency: per-operation connections + WAL.
- DM availability: assignees must DM-start the bot to receive notifications; handle failures gracefully and surface status.
- Callback size limits: keep callback_data compact.
- Timezones: store UTC for timestamps; use configured TZ only for display (no date logic in MVP).

## Definition of Done (per phase)
- All acceptance criteria for the phase met.
- Deployed on GCE, service active, basic manual test passes.
- Notes captured in `comms/log.md`; spec archived when approved.
