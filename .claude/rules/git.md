# rules/git.md
# Git and PR standards for restaurant_scraper.

## Commits
- Commit immediately upon task completion — at least once per work session.
- One feature per commit / PR; keep PRs under ~150 lines of diff where possible.
- Commit message format: `<type>: <short description>` (feat, fix, refactor, test, docs, chore).

## Branches
- All Claude work goes on branches prefixed `claude/`.
- Never push directly to main without explicit user approval.

## PR standards
- Squash merge only — keeps history linear.
- PR body must include: Summary bullets + Test plan checklist.
