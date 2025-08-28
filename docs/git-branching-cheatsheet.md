# Git Branching Cheatsheet (UsualSuspects)

This is a practical list of commands with short comments. Use it locally and on the server. Our active feature branch is `feature/mini-app-mvp`.

## Basics — Where am I?
- Current branch: `git branch --show-current`
- Quick status: `git status`
- Last commits: `git log --oneline -n 10 --decorate`
- Current commit id: `git rev-parse --short HEAD`
- Pretty graph: `git log --oneline --decorate --graph --all -n 20`

## Getting the Repo (new computer)
- Clone: `git clone <repo-url>`
- Enter dir: `cd fordfencers_telegram`
- Fetch all branches: `git fetch --all --prune`
- Switch to branch (tracks remote): `git switch -c feature/mini-app-mvp --track origin/feature/mini-app-mvp`
  - If already exists locally: `git switch feature/mini-app-mvp`

## Working on the Branch
- Ensure correct branch: `git branch --show-current` → should say `feature/mini-app-mvp`
- Pull latest: `git pull` (when already tracking upstream)
- Stage + commit: `git add -A && git commit -m "message"`
- Push first time (set upstream): `git push -u origin feature/mini-app-mvp`
- Push updates: `git push`

## Juggling Branch and Main
- Switch to main: `git switch main`
- Update main: `git pull`
- Go back to feature: `git switch feature/mini-app-mvp`
- Bring main into feature (merge): `git switch feature/mini-app-mvp && git merge origin/main`
- Or rebase feature on main (clean history): `git fetch origin && git rebase origin/main`
  - If conflicts: resolve files, then `git add -A && git rebase --continue`
  - Abort rebase: `git rebase --abort`

## Checking Which Version You’re On
- Branch + commit: `echo "$(git branch --show-current)@$(git rev-parse --short HEAD)"`
- Describe (tags if any): `git describe --always --dirty --tags`

## Quick Safety Tips
- Commit small and often (easy rollback).
- Don’t force-push to `main`; use PRs from the feature branch.
- Use `git stash` to shelve uncommitted changes when switching branches: `git stash push -m "wip"` then `git stash pop` later.
- To see what you changed: `git diff` (unstaged) and `git diff --staged` (staged).

## Using Git Properly on the Server
- Verify location: `pwd` should be your app dir (e.g., `/opt/fordfencers`).
- Verify user: use the `bot` user if you followed our DO guide.
- Check current branch/commit: `git branch --show-current && git rev-parse --short HEAD`.
- Pull latest for current branch: `git pull`.
- If Git complains about directory ownership: `git config --global --add safe.directory /opt/fordfencers`.
- After pulling, restart services if needed:
  - Bot: `sudo systemctl restart fordfencers-bot`
  - Web: `sudo systemctl restart fordfencers-web`

## Tracking/Setting Upstream Manually
- See remotes: `git remote -v`
- Set upstream for current branch: `git push -u origin $(git branch --show-current)`
- Change remote URL: `git remote set-url origin <new-url>`

## Common “Unknown Unknowns” (Fast Answers)
- “I’m on the wrong branch”: `git switch feature/mini-app-mvp` (stash first if you have changes).
- “I have local changes I don’t want”: `git reset --hard HEAD` (danger: discards local changes).
- “Conflicts after merge/rebase”: open files with conflict markers, then `rg -n "^<<<<<<<|^=======$|^>>>>>>>"` (requires ripgrep), resolve → `git add -A` → continue (`git merge --continue` or `git rebase --continue`).
- “My local is behind origin”: `git fetch --all --prune && git status && git pull`.
- “Create a new feature branch”: `git switch -c feature/something && git push -u origin feature/something`.

## TL;DR Flow (Day to Day)
1) `git switch feature/mini-app-mvp`
2) `git pull`
3) make changes
4) `git add -A && git commit -m "..."`
5) `git push`

Optional sync with main periodically:
- `git fetch origin && git rebase origin/main` (or merge if you prefer)

