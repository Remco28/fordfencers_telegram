# Task: Bot Branding Unification — Display Name vs Handle

Author: Architect
Status: SPEC READY
Priority: High
Scope: Code + Docs

## Objective
Standardize the bot’s public-facing identity across code and docs:
- Display name shown to users: "Ford-Fencers-Bot"
- Official Telegram handle/username: "@UsualSuspects_bot"

This removes confusion between the visible name and the unique handle used in links and prompts.

## User Stories
- As a group member, when the bot responds, I see "Ford-Fencers-Bot" in user-facing text.
- As a user prompted to DM the bot, I get a correct, clickable handle "@UsualSuspects_bot".
- As an operator, startup logs clearly show the display name and handle being used.

## Changes Required

### Code
- File: `config.py`
  - Defaults:
    - `BOT_DISPLAY_NAME` default → "Ford-Fencers-Bot"
    - `BOT_HANDLE` default → "@UsualSuspects_bot"
  - Add minimal normalization/validation for `BOT_HANDLE`:
    - Ensure it starts with `@`.
    - Log at INFO if a non-standard value is provided (case-insensitive compare to `@UsualSuspects_bot`).
  - Pseudocode:
    - `handle = os.getenv("BOT_HANDLE", "@UsualSuspects_bot")`
    - `if not handle.startswith("@"): handle = "@" + handle`
    - `if handle.lower() != "@usualsuspects_bot": logging.info("Using non-standard handle: %s", handle)`

- File: `app.py`
  - Replace hardcoded startup banner string with settings-based one:
    - From: `"Starting Ford-Fencers-Bot {VERSION}"`
    - To: `f"Starting {settings.BOT_DISPLAY_NAME} {VERSION} ({settings.BOT_HANDLE})"`

- Files: `handlers/commands.py` (confirm only)
  - Ensure all user-facing strings use `settings.BOT_DISPLAY_NAME` and `settings.BOT_HANDLE` (no hardcoded names). Current usage looks correct; keep as-is.

### Documentation
- File: `docs/gce-vm-setup.md`
  - Keep title and examples consistent with display name "Ford-Fencers-Bot".
  - Ensure unit file example `Description` reads "Ford-Fencers-Bot".

- File: `docs/digitalocean-setup.md`
  - Unify branding: examples should state display name "Ford-Fencers-Bot" while keeping `BOT_HANDLE=@UsualSuspects_bot`.
  - Update any lingering "UsualSuspects Bot" display-name references to "Ford-Fencers-Bot".
  - Keep service/unit descriptions consistent; prefer "Ford-Fencers-Bot".

- File: `docs/ROADMAP.md`
  - Title: "Ford-Fencers-Bot – Roadmap" (or keep if already correct).

## Constraints
- Do not hardcode names or handles in handlers; rely on `settings` only.
- Defaults must reflect the official identity (display name: Ford-Fencers-Bot, handle: @UsualSuspects_bot), but allow overrides via env for forks.
- No behavior changes beyond logging/message text and doc consistency.

## Expected Behavior
- Fresh run without env overrides logs: `Starting Ford-Fencers-Bot vX.Y.Z (@UsualSuspects_bot)`.
- Group and DM messages render the display name via `settings.BOT_DISPLAY_NAME`.
- All DM prompts and links reference `settings.BOT_HANDLE` → "@UsualSuspects_bot".

## Acceptance Criteria
- Code grep shows no hardcoded occurrences of "UsualSuspects Bot" or `@UsualSuspects_bot` outside `config.py` defaults and docs.
- Code grep shows no hardcoded "Ford-Fencers" in handlers; only in defaults and logs constructed from `settings`.
- Updated docs reflect the correct pairing: display name Ford-Fencers-Bot, handle @UsualSuspects_bot.
- `app.py` startup log includes both display name and handle from `settings`.

## Validation Steps
1) Run the bot locally with no `BOT_DISPLAY_NAME`/`BOT_HANDLE` env set.
   - Observe startup log message with Ford-Fencers-Bot and @UsualSuspects_bot.
2) Issue `/start` in DM and in a group; verify user-facing strings show the display name and, where relevant, the handle link.
3) Optional: Set `BOT_HANDLE=UsualSuspects_bot` (no `@`) and verify it is auto-normalized with an INFO log noting the non-standard value.

## Notes
- This task does not modify conversation flows or features.
- If separate brand assets (icons, descriptions) exist in stores or profiles, update them manually in Telegram as needed.
