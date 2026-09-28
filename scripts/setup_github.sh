#!/usr/bin/env bash
# Create a Projects (v2) board for a learning-path repo, link it, and
# optionally create one tracker issue per learner.
#
# Requires: GitHub CLI (`gh`), already authenticated (`gh auth login`) with
# the `project` scope (`gh auth refresh -s project` if missing).
#
# Usage:
#   ./setup_github.sh --repo <owner>/<repo> --title "<Project title>" [--owner <org-or-user>] [--employees "Jane Doe,John Smith"]
#
# --owner defaults to the part before "/" in --repo. Pass it explicitly when
# creating the project under an org that differs from the repo's namespace.

set -euo pipefail

REPO=""
TITLE=""
OWNER=""
EMPLOYEES=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --owner) OWNER="$2"; shift 2 ;;
    --employees) EMPLOYEES="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$REPO" || -z "$TITLE" ]]; then
  echo "Usage: $0 --repo <owner>/<repo> --title \"<Project title>\" [--owner <org-or-user>] [--employees \"Name1,Name2\"]" >&2
  exit 1
fi

if [[ -z "$OWNER" ]]; then
  OWNER="${REPO%%/*}"
fi

echo "Creating project '$TITLE' under $OWNER..."
PROJECT_JSON=$(gh project create --owner "$OWNER" --title "$TITLE" --format json)
PROJECT_NUMBER=$(echo "$PROJECT_JSON" | grep -o '"number":[0-9]*' | head -1 | grep -o '[0-9]*')
PROJECT_URL=$(echo "$PROJECT_JSON" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "Linking project #$PROJECT_NUMBER to $REPO..."
gh project link "$PROJECT_NUMBER" --owner "$OWNER" --repo "$REPO"

echo ""
echo "Project board: $PROJECT_URL"

if [[ -n "$EMPLOYEES" ]]; then
  ISSUE_LABEL=$(grep '^labels:' "$(git -C . rev-parse --show-toplevel 2>/dev/null || echo .)/.github/ISSUE_TEMPLATE"/*.md 2>/dev/null | head -1 | sed 's/^labels: *//')
  ISSUE_LABEL="${ISSUE_LABEL:-learning-path}"
  TEMPLATE_FILE=$(ls .github/ISSUE_TEMPLATE/*.md 2>/dev/null | head -1)
  if [[ -z "$TEMPLATE_FILE" ]]; then
    echo "Warning: no issue template found under .github/ISSUE_TEMPLATE/ in the current directory; skipping issue creation." >&2
  else
    # Strip YAML frontmatter and the leading HTML comment to get the body.
    BODY=$(awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "$TEMPLATE_FILE" | sed '/^<!--/,/^-->/d')
    IFS=',' read -ra NAMES <<< "$EMPLOYEES"
    for RAW_NAME in "${NAMES[@]}"; do
      NAME=$(echo "$RAW_NAME" | sed 's/^ *//;s/ *$//')
      echo "Creating issue for $NAME..."
      ISSUE_URL=$(gh issue create --repo "$REPO" --title "[Learning Path] $NAME" --body "$BODY" --label "$ISSUE_LABEL")
      echo "  $ISSUE_URL"
      gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$ISSUE_URL" >/dev/null
    done
  fi
fi

echo ""
echo "Done. Due dates on each issue fill in automatically within seconds of creation"
echo "(via .github/workflows/set-due-dates.yml — make sure it's pushed to $REPO first)."
