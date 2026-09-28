---
name: learning-path-tracker
description: Set up a GitHub-based progress tracker (per-learner issue checklist with auto-filled due dates, plus a project board) from a learning path document such as a PDF, Word doc, or Markdown file. Use when the user wants to track employees'/learners' progress through a training or learning path in GitHub, or mentions turning a learning-path document into a tracker, checklist, or board.
---

This skill wraps the toolkit in this repo (`learning-path-agent`). Read
`../../../AGENT_PROMPT.md` (relative to this file — i.e. the `AGENT_PROMPT.md` at
the repo root) and follow it exactly, step by step:

1. Confirm you have `SOURCE_PATH` (the learning path document), `REPO_PATH` (local
   clone of the target repo), and `REPO_SLUG` (its `owner/name` on GitHub) — ask the
   user for whichever is missing rather than guessing.
2. Extract the source document into a `learning-path.yaml` matching
   `schema/learning-path.schema.yaml` (repo root), using
   `examples/copilot-studio-learning-path.yaml` as a reference for the level of
   detail expected.
3. Run `python scripts/generate.py --input learning-path.yaml --repo-path REPO_PATH`
   (paths relative to this repo's root — run from there, or use absolute paths).
4. Show the user the generated issue template, then commit and push (with
   confirmation if it's a shared/company repo).
5. Run `./scripts/setup_github.sh --repo REPO_SLUG --title "<Title> — Tracker"`
   (add `--employees "Name1,Name2"` if the user gave learner names) to create the
   project board and, optionally, the tracker issues.
6. Report back the repo URL, project board URL, and any issue URLs created.

All commands assume the working directory is this toolkit's repo root (where
`scripts/`, `schema/`, `templates/`, and `examples/` live) — if running from
elsewhere, use absolute paths to those files instead.
