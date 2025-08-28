# Tech Debt Quick Fixes — Branding, Chat Selection, Ask Aggregation

Author: Architect
Date: 2025-08-28
Status: SPEC READY

## Objectives
- Unify bot branding and handle across code and docs.
- Make chat selection deterministic and explicit via `PRIMARY_CHAT_ID`.
- Remove fragile SQL string aggregation from `get_all_open_asks`.
- Harden DM UX by preparing for Mini App entry (config keys only; no UI changes yet).

## Scope
This spec focuses on low-risk, high-value fixes to the existing bot code. No Mini App implementation in this task — just configuration groundwork and safer data access.

## Changes Required

Configuration
- File: `config.py`
  - Add setting: `BOT_DISPLAY_NAME: str` (e.g., "UsualSuspects Bot").
  - Add setting: `BOT_HANDLE: str` (e.g., "@UsualSuspects_bot").
  - Add setting: `PRIMARY_CHAT_ID: int | None` — explicit family/group chat id for group-scoped operations. If unset, fall back to current behavior (DM chat id where applicable).
  - Add setting: `WEBAPP_URL: str | None` — optional; when set, we can show an inline “Open App” button in DM `/start` (actual button change deferred to Mini App task).

Branding Unification
- Files: `handlers/commands.py`, `docs/` where the bot name/handle appears.
  - Replace hardcoded strings like "UsualSuspects Bot" and `@UsualSuspects_bot` with `settings.BOT_DISPLAY_NAME` and `settings.BOT_HANDLE`.
  - Ensure responses that instruct users to DM the bot use `settings.BOT_HANDLE`.

Deterministic Chat Selection
- Files: `handlers/asks.py`, any code referencing `next(iter(settings.ALLOWED_CHAT_IDS))`.
  - Replace non-deterministic set iteration with: if `settings.PRIMARY_CHAT_ID` is set, use it; otherwise use `update.effective_chat.id` (DM context).
  - Keep existing `ALLOWED_CHAT_IDS` checks for authorization; `PRIMARY_CHAT_ID` only selects the default group context for storing/reading asks.

Ask Aggregation Refactor
- File: `db.py`
  - Function: `get_all_open_asks(chat_id: int) -> List[Dict]`
  - Replace `GROUP_CONCAT` approach with row-wise fetch and Python-side grouping to avoid delimiter parsing bugs.
  - New query shape (illustrative):
    ```sql
    SELECT a.id as ask_id, a.text, a.requester_name,
           aa.assignee_name, aa.status
    FROM asks a
    JOIN ask_assignees aa ON a.id = aa.ask_id
    WHERE a.chat_id = ? AND a.status = 'open'
    ORDER BY a.created_at DESC, a.id, aa.id
    ```
  - Group by `ask_id` in Python and build `assignees: List[Tuple[name, status]]`.

Self‑Assign Rule (Future‑proofing)
- Ensure requester cannot self-assign:
  - In the DM flow (current bot): when building the roster for selection, exclude `requester_id`.
  - On submit, validate and strip `requester_id` if present; if removal empties selection, show an error.
  - Note: Mini App task will mirror this in API and UI; include in acceptance tests here for the DM flow.

Logging Consistency
- Ensure logs for commands and key actions include `user_id` and `chat_id` in a consistent format.

## Expected Behavior
- Messages mentioning the bot show the configured handle/name; no stray hardcoded names.
- All ask creation/listing uses a deterministic group chat via `PRIMARY_CHAT_ID` when set.
- Listing all open asks produces correct assignee lists even if names contain commas/colons.
- Requesters cannot assign tasks to themselves in the DM flow.

## Acceptance Criteria
- `config.py` exposes `BOT_DISPLAY_NAME`, `BOT_HANDLE`, `PRIMARY_CHAT_ID`, `WEBAPP_URL` (optional).
- No occurrences of hardcoded bot name/handle remain in Python files.
- `handlers/asks.py` uses `PRIMARY_CHAT_ID` where applicable; no `next(iter(...))` remains.
- `db.get_all_open_asks` groups in Python; no `GROUP_CONCAT` or string splitting.
- DM flow prevents self-assign (both UI exclusion and server-side guard).
- Logs for `/start`, `/ask`, `/my_asks`, `/asks_all`, and ask submission include `user_id` and `chat_id`.

## Pseudocode

Deterministic chat selection:
```
chat_id = settings.PRIMARY_CHAT_ID if settings.PRIMARY_CHAT_ID else update.effective_chat.id
```

get_all_open_asks (Python grouping):
```
rows = conn.execute(SQL, (chat_id,)).fetchall()
by_id = {}
for ask_id, text, requester_name, assignee_name, status in rows:
    by_id.setdefault(ask_id, {"ask_id": ask_id, "text": text, "requester_name": requester_name, "assignees": []})
    by_id[ask_id]["assignees"].append((assignee_name, status))
return list(by_id.values())
```

Self‑assign prevent (roster):
```
roster = [(uid, name) for (uid, name) in db.get_roster() if uid != requester_id]
```

Validation on submit:
```
assignees = [uid for uid in selected if uid != requester_id]
if not assignees: error("Select at least one person other than yourself")
```

## Notes
- Do not implement Mini App UI or endpoints here; only add `WEBAPP_URL` to config for the next task.
- Keep changes minimal and aligned with existing code style.

