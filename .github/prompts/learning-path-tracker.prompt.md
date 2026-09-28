---
mode: agent
description: Set up a GitHub progress tracker (per-learner checklist with auto-filled due dates, plus a project board) from a learning path document.
---

Follow `AGENT_PROMPT.md` at the repo root, step by step, to set up a learning path
progress tracker.

Before starting, confirm you have from the user:
- `SOURCE_PATH` — the learning path document to extract (PDF, Word, Markdown, etc.)
- `REPO_PATH` — local clone of the target repo the tracker should live in
- `REPO_SLUG` — that repo's `owner/name` on GitHub
- Optionally, learner names (and GitHub usernames) to create tracker issues for

Then: extract the source into `learning-path.yaml` per
`schema/learning-path.schema.yaml`, run `scripts/generate.py`, show the user the
generated issue template, commit/push with their confirmation, run
`scripts/setup_github.sh` to create the project board (and issues, if names were
given), and report back the repo/project/issue URLs.
