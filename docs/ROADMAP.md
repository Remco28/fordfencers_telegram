# Ford-Fencers-Bot – Roadmap

## Vision
- DM-first assistant for lightweight “Asks” (ask <person> to do <thing>), with a clean, tap-first UI via Telegram Mini App. Keep the group chat tidy; low maintenance, safe-by-default.

## Guiding Principles
- Ship incremental slices; optimize for ease of setup first, polish later.
- Prefer correctness and resilience over features.
- Store UTC in DB; present in local timezone.
- Use parameterized SQL; avoid global DB state in async.
- Keep bot handlers lean; move rich UX to Mini App.

## Milestones & Phases

### Completed – Asks MVP (bot-only)
- DM flows to create an Ask, select multiple assignees, and submit text.
- “My Asks” list with Done + confirmation; requester DM notification on completion.
- “All Open Asks” compact DM summary.
- SQLite schema: `users`, `asks`, `ask_assignees`; WAL + indexes.

### Phase 0 – Mini App Prep (no user impact)
- Confirm domain + HTTPS for WebApp URL.
- Decide static hosting vs same-VM serving; add CSP policy baseline.
- Define Mini App routes, data contracts, and auth (initData verification).
 - Infra note: We are transitioning to DigitalOcean (DO) for domain/DNS and hosting. GCP artifacts remain temporarily for reference only.

### Phase 1 – Mini App MVP (DM-only)
- Implement Telegram WebApp shell (Home, My Assignments, New Ask basic flow).
- Verify `initData` and issue session token; add minimal backend API for roster, my assignments, create ask.
- Configure DM Menu Button (`MenuButtonWebApp`) and send a welcome DM with inline “Open App”.
- No group interactions yet; DM-only entry.

### Phase 2 – Quality & Polish
- Telegram theme integration, haptics, in-app back button.
- Loading/error states, basic analytics/metrics.
- Hardening: rate limits, logs, alerts.

### Phase 3 – Gradual Group Surfacing (future)
- Pin a single “Open App” message in group.
- Add inline “Open App” responses to mentions/keywords (lightweight, non-intrusive).

### Phase 4 – Feature Expansion
- Add additional flows (payments, multi-step forms, admin tools) as needed.
- Optional: explore Attachment Menu application (requires Telegram approval).

## Workstreams
- Bot: Handlers, keyboards, compact callback protocol (`ak:*`), DM onboarding, Menu Button config.
- WebApp: Static SPA using `telegram-web-app.js`; pages for Home, My Assignments, New Ask.
- Backend: FastAPI service for auth (initData verification) and minimal APIs.
- Data: Reuse SQLite; expose safe read/write endpoints used by the WebApp.
- DevEx: Config, logging, deployment, docs.

## Infra Direction (Early Stage)
- Provider: Move to DigitalOcean for simplicity and predictable pricing.
- Domain/DNS: Purchase/host DNS on DO; use a subdomain like `app.<domain>` for the Mini App.
- Hosting:
  - Short term: Bot continues running via polling on a VM (GCE or DO), Mini App (static + FastAPI) behind HTTPS (Caddy/NGINX) on the same VM or DO App Platform.
  - Near term: Consolidate both bot and Mini App to a DO Droplet; deprecate GCP docs.

## Initial Task Breakdown (upcoming)
- Phase 1 spec for Mini App MVP (this file in `comms/tasks/`).
- Add backend auth verification + endpoints (roster, assignments, create ask).
- Create static Mini App shell and integrate with backend.
- Configure DM Menu Button to open the WebApp; send welcome DM with inline button.

## Risks & Mitigations
- SQLite concurrency: per-operation connections + WAL.
- DM availability: assignees must DM-start the bot to receive notifications; handle failures gracefully.
- WebApp auth: strictly verify `initData` HMAC; short-lived sessions.
- Latency/cold starts on free tier: serve static assets efficiently; keep APIs lean.

## Definition of Done (per phase)
- All acceptance criteria for the phase met.
- Deployed on GCE, service active, basic manual test passes.
- Notes captured in `comms/log.md`; spec archived when approved.
