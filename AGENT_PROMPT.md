# Learning Path Tracker Agent

You are setting up a GitHub-based progress tracker for a learning path. This works
the same way regardless of which AI assistant or model is running it — you (the AI)
handle the one step that needs judgment (reading the source material), and everything
else is done by the deterministic scripts in this toolkit. Follow these steps in order.

## Inputs you need from the user

Before starting, make sure you have:

1. **`SOURCE_PATH`** — path (or pasted content) of the learning path document: a PDF,
   Word doc, Markdown file, web page, whatever it is.
2. **`REPO_PATH`** — path to the local clone of the target GitHub repo (or ask the
   user to create/clone one first if it doesn't exist yet).
3. **`REPO_SLUG`** — the repo's `owner/name` on GitHub (needed later for `gh` commands).
4. Optionally, a list of learner names (and GitHub usernames, if you want issues
   auto-assigned) to create tracker issues for right away.

If any of these are missing, ask before proceeding — don't guess a repo location or
invent learner names.

## Step 1 — Extract the learning path into the canonical YAML format

Read `schema/learning-path.schema.yaml` in this toolkit for the exact fields required.
Read `SOURCE_PATH` and produce a file (e.g. `learning-path.yaml`) matching that schema:

- `title`, `target_credential` (if any), `total_weeks` (the intended time budget —
  ask the user if the source document doesn't state one).
- `phases`: preserve the source document's own phase/module breakdown and ordering.
  Each phase needs a `duration_days` estimate — use the source's own time estimates
  if given (convert "half a day" → 0.5, "two to three days" → 2.5, etc.); otherwise
  estimate proportionally to the phase's apparent scope.
- `steps` within each phase: one entry per concrete, checkable action (a module to
  complete, a doc to read, an exercise to do) — not every sentence in the source.
  Preserve links to source material as Markdown links inside `text`.
- Use `substeps` for a step's own internal checklist (e.g. the stages of a single
  workshop), not for unrelated steps.
- Add a `certification` block only if the source document names an optional
  certification/credential path.

Look at `examples/copilot-studio-learning-path.yaml` for a fully worked example of
this extraction from a real learning-path PDF.

Do not skip this step's judgment calls to the script — `generate.py` does no
interpretation of prose; it only turns already-structured YAML into GitHub files.

## Step 2 — Generate the GitHub artifacts

Run:

```
python scripts/generate.py --input learning-path.yaml --repo-path REPO_PATH
```

This writes into `REPO_PATH`:
- `.github/ISSUE_TEMPLATE/learning-path-progress.md` — the per-learner checklist template
- `.github/workflows/set-due-dates.yml` — a GitHub Action that auto-fills due dates
  on every new issue created from that template, based on business-day offsets
  across the `total_weeks` schedule
- `README.md` — a short explainer of how the tracker works

Show the user the generated issue template before moving on, in case they want to
adjust wording, add/remove steps, or change `total_weeks` and regenerate (`--force`
to overwrite).

## Step 3 — Commit and push

```
cd REPO_PATH
git add .github README.md
git commit -m "Add <title> learning path progress tracker"
git push
```

Confirm with the user before pushing if this is a shared/company repo you don't
normally push to directly.

## Step 4 — Create the project board (and optionally the learner issues)

Requires the GitHub CLI (`gh`), authenticated with the `project` scope
(`gh auth status`; if missing, `gh auth refresh -s project`).

```
./scripts/setup_github.sh --repo REPO_SLUG --title "<Title> — Tracker" [--employees "Jane Doe,John Smith"]
```

This creates a Projects (v2) board, links it to the repo, and — if `--employees` was
given — creates one tracker issue per name and adds it to the board. Without
`--employees`, just report the project board URL and tell the user how to create
issues manually (Issues → New issue → pick the template).

If the user gave you specific GitHub usernames to assign, use
`gh issue edit <issue-url> --add-assignee <username>` after creation.

## Step 5 — Report back

Give the user:
- The repo URL and project board URL
- Any issue URLs created
- A one-line reminder that due dates fill in automatically within seconds of an
  issue being opened — no manual date entry needed
