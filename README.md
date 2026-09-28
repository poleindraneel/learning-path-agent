# Learning Path Agent

A reusable toolkit for turning any learning path document (PDF, Word, Markdown,
whatever) into a GitHub-based progress tracker: a per-learner issue checklist with
auto-filled due dates, and a project board to see everyone's progress at a glance.

It was built by generalizing a one-off setup done for a Copilot Studio learning path,
so it can be reused for the next tool/tech without redoing the work by hand.

## Design: split what needs a model from what doesn't

- **Reading and understanding the source document** needs judgment — an AI assistant
  (any capable one: Claude, GPT, Copilot, Gemini, ...) does this once per learning
  path, guided by [`AGENT_PROMPT.md`](./AGENT_PROMPT.md).
- **Generating GitHub artifacts from structured data** doesn't need a model at all —
  it's a plain Python/Bash script (`scripts/generate.py`, `scripts/setup_github.sh`).

The two are decoupled through one file format: [`schema/learning-path.schema.yaml`](./schema/learning-path.schema.yaml).
This is what makes the toolkit reproducible across different AI tools — the AI's job
is narrow (produce that one YAML file correctly), and everything downstream is
deterministic and identical no matter which model wrote the YAML.

## How to use this

### With an AI coding assistant (Claude Code, Cursor, Copilot Workspace, etc.)

1. Give the assistant this folder, the path to your learning path source document,
   and the path/URL of the target GitHub repo.
2. Tell it: **"Follow AGENT_PROMPT.md to set up a tracker for this learning path."**
3. It extracts the content into a YAML file, runs the generator, and (with your
   confirmation) commits, pushes, and creates the project board and issues.

### By hand, without an AI assistant

1. Copy [`examples/copilot-studio-learning-path.yaml`](./examples/copilot-studio-learning-path.yaml)
   as a starting point and edit it to describe your learning path (see the schema
   comments for field meanings).
2. `pip install pyyaml`
3. `python scripts/generate.py --input your-learning-path.yaml --repo-path /path/to/repo`
4. Commit and push the generated `.github/` files.
5. `./scripts/setup_github.sh --repo owner/repo --title "Your Tracker" --employees "Name1,Name2"`

## Requirements

- Python 3 with `pyyaml` (`pip install pyyaml`)
- [GitHub CLI](https://cli.github.com/) (`gh`), authenticated with the `project` scope
  (`gh auth refresh -s project` if you're missing it)
- Write access to the target repo (or someone with access runs steps 3–5 for you)

## Folder contents

| Path | Purpose |
|---|---|
| `AGENT_PROMPT.md` | Instructions for an AI assistant to run this end-to-end |
| `schema/learning-path.schema.yaml` | The canonical input format, documented |
| `examples/copilot-studio-learning-path.yaml` | A fully worked example |
| `templates/set-due-dates.yml.tmpl` | The GitHub Action template that auto-fills due dates |
| `scripts/generate.py` | Generates the issue template, workflow, and README into a target repo |
| `scripts/setup_github.sh` | Creates the Projects (v2) board and (optionally) learner issues |

## Handing this off

This whole folder is self-contained and has no dependency on any specific repo or
model — copy it into a shared company location (or its own git repo) and hand it to
a colleague, or point any AI coding tool at it. The only per-run inputs are the
source document and the target repo.
