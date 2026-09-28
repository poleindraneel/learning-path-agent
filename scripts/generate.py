#!/usr/bin/env python3
"""
Generate a GitHub issue template + due-date-automation workflow + README from a
canonical learning-path YAML file (see schema/learning-path.schema.yaml).

Usage:
    python generate.py --input path/to/learning-path.yaml --repo-path /path/to/target/repo [--force]

This script is intentionally deterministic and model-agnostic: it does no
interpretation of free-form text. Turning a source document (PDF, Word, web
page, ...) into the input YAML is the one step that needs an AI assistant or a
human — see ../AGENT_PROMPT.md.

Requires PyYAML: pip install pyyaml
"""
import argparse
import math
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: run `pip install pyyaml` and try again.")

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "learning-path"


def load_learning_path(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    required = ["title", "total_weeks", "phases"]
    missing = [k for k in required if k not in data]
    if missing:
        sys.exit(f"Input YAML is missing required field(s): {', '.join(missing)}")
    if not data["phases"]:
        sys.exit("Input YAML must have at least one phase.")

    data.setdefault("label", slugify(data["title"]))
    data.setdefault("target_credential", None)
    return data


def collect_sections(data):
    """Phases plus the optional trailing certification block, as one list."""
    sections = list(data["phases"])
    if data.get("certification"):
        sections.append(data["certification"])
    for s in sections:
        s.setdefault("duration_days", 1)
        s.setdefault("steps", [])
        s.setdefault("note", None)
    return sections


def assign_offsets(sections, total_business_days):
    """
    Mutates each section in place, adding:
      - section["_end_offset"]: business-day offset the whole phase is due by
      - each leaf step dict gets "_offset": its own due-date offset

    A "leaf" step is one with no substeps; a step WITH substeps is due at the
    phase's end offset, while its substeps get their own interpolated offsets
    within the phase's [start_offset, end_offset] range.
    """
    total_duration = sum(s["duration_days"] for s in sections) or 1
    cumulative = 0.0
    last_index = len(sections) - 1

    for i, section in enumerate(sections):
        start_offset = round(cumulative / total_duration * total_business_days)
        cumulative += section["duration_days"]
        if i == last_index:
            end_offset = total_business_days - 1
        else:
            end_offset = round(cumulative / total_duration * total_business_days)
        end_offset = max(end_offset, start_offset)
        section["_end_offset"] = end_offset

        leaves = []
        for step in section["steps"]:
            if step.get("substeps"):
                leaves.extend(step["substeps"])
            else:
                leaves.append(step)

        n = len(leaves)
        for idx, leaf in enumerate(leaves):
            if n <= 1:
                leaf["_offset"] = end_offset
            else:
                span = end_offset - start_offset
                leaf["_offset"] = start_offset + round(idx * span / (n - 1))


def render_step_line(step, indent=""):
    offset = step["_offset"]
    return f"{indent}- [ ] {step['text']} — Due {{{{due:{offset}}}}}"


def render_section(section):
    lines = [f"## {section['name']} ({section['duration_days']}d) — Due {{{{due:{section['_end_offset']}}}}}", ""]
    for step in section["steps"]:
        if step.get("substeps"):
            lines.append(f"- [ ] {step['text']} — Due {{{{due:{section['_end_offset']}}}}}")
            for sub in step["substeps"]:
                lines.append(render_step_line(sub, indent="  "))
        else:
            lines.append(render_step_line(step))
    if section.get("note"):
        lines.append("")
        lines.append(f"*({section['note']})*")
    return "\n".join(lines)


def render_issue_template(data, sections):
    header = f"""---
name: {data['title']} — Progress Tracker
about: Track one person's progress through the {data['title']} learning path
title: "[Learning Path] "
labels: {data['label']}
assignees: ''
---

<!--
Set the issue title to the employee's name, e.g. "[Learning Path] Jane Doe",
and assign the issue to them so their avatar shows up on the project board.
Tick boxes as each step is completed — GitHub tracks the % automatically.

Due dates below are placeholders like {{{{due:3}}}} — a GitHub Action fills them
in with real dates automatically right after you submit this issue, counting
business days from today across the {data['total_weeks']}-week schedule.
Do not edit the {{{{due:N}}}} placeholders by hand.
-->
"""
    body_lines = [header]
    if data.get("target_credential"):
        body_lines.append(f"Target credential: **{data['target_credential']}**")
    body_lines.append(f"Target effort: ~{data['total_weeks']} weeks — due dates auto-filled below")
    body_lines.append("")
    for section in sections:
        body_lines.append(render_section(section))
        body_lines.append("")
    return "\n".join(body_lines).rstrip() + "\n"


def render_workflow(data):
    tmpl_path = os.path.join(TOOL_DIR, "templates", "set-due-dates.yml.tmpl")
    with open(tmpl_path, "r", encoding="utf-8") as f:
        tmpl = f.read()
    return tmpl.replace("__LABEL__", data["label"])


def render_readme(data):
    return f"""# {data['title']} — Progress Tracker

{f"Target credential: **{data['target_credential']}**" if data.get('target_credential') else ''}

## How progress tracking works

Each learner gets their own GitHub Issue created from the **"{data['title']} — Progress
Tracker"** template. The issue body is a Markdown checklist of every step in the path;
GitHub renders checkboxes anyone with write access can tick, shows a completion
percentage automatically, and a GitHub Action fills in real due dates the moment the
issue is created (see `.github/workflows/set-due-dates.yml`).

### Onboard a new learner

1. Go to **Issues → New issue → {data['title']} — Progress Tracker**.
2. Set the title to their name, e.g. `[Learning Path] Jane Doe`, and assign the issue to them.
3. Add the issue to the project board for this learning path.
4. Due dates fill in automatically within seconds; tick boxes as steps are completed.

Generated by [learning-path-agent](../LearningPathAgent) from `{os.path.basename(data.get('_source', 'learning-path.yaml'))}`.
"""


def write_file(path, content, force):
    if os.path.exists(path) and not force:
        print(f"  skip (exists, use --force to overwrite): {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  wrote: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to the learning-path YAML file")
    parser.add_argument("--repo-path", required=True, help="Path to the target git repo")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    data = load_learning_path(args.input)
    data["_source"] = args.input
    sections = collect_sections(data)
    total_business_days = max(round(data["total_weeks"] * 5), 1)
    assign_offsets(sections, total_business_days)

    print(f"Generating tracker for '{data['title']}' ({total_business_days} business days)...")
    write_file(
        os.path.join(args.repo_path, ".github", "ISSUE_TEMPLATE", "learning-path-progress.md"),
        render_issue_template(data, sections),
        args.force,
    )
    write_file(
        os.path.join(args.repo_path, ".github", "workflows", "set-due-dates.yml"),
        render_workflow(data),
        args.force,
    )
    write_file(
        os.path.join(args.repo_path, "README.md"),
        render_readme(data),
        args.force,
    )

    print("\nNext steps:")
    print("  1. Review the generated files, then commit and push them to the repo.")
    print("  2. Run scripts/setup_github.sh to create the project board (see README.md).")
    print("  3. Create one issue per learner from the new issue template.")


if __name__ == "__main__":
    main()
