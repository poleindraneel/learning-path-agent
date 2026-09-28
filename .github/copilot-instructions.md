# Repository instructions for GitHub Copilot

This repo is a toolkit for turning a learning path document (PDF, Word, Markdown,
web page) into a GitHub-based progress tracker: a per-learner issue checklist with
auto-filled due dates, and a Projects (v2) board.

If the user asks you to set up a progress tracker, checklist, or board for a
learning path, training, or onboarding document — whether in this repo or another
target repo — **read and follow `AGENT_PROMPT.md` at the repo root, step by step.**
Do not skip straight to writing files yourself; that file specifies the exact
canonical YAML format (`schema/learning-path.schema.yaml`) the generator script
(`scripts/generate.py`) expects, and the order of operations (extract → generate →
commit/push → create project board and issues → report back).

Key things to keep in mind:
- Ask for `SOURCE_PATH` (the learning path document), `REPO_PATH` (local clone of
  the target repo), and `REPO_SLUG` (`owner/name`) if not already given — don't
  guess a repo location or invent learner names.
- The extraction step (source document → `learning-path.yaml`) is the only part
  that needs judgment; `scripts/generate.py` and `scripts/setup_github.sh` are
  deterministic and should be run as-is, not reimplemented.
- Confirm with the user before pushing to a shared/company repo, and before
  creating issues assigned to real people.
