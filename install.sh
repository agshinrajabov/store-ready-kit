#!/usr/bin/env bash
# Install the store-ready-kit skills for Claude Code (or any agent that reads SKILL.md folders).
#
#   ./install.sh                 symlink every skill into ~/.claude/skills/ (updates with `git pull`)
#   ./install.sh --copy          copy instead of symlink
#   ./install.sh --dest DIR      install somewhere else (e.g. a project's .claude/skills)
#   ./install.sh --only store-audit,submission-pilot
#   ./install.sh --uninstall     remove what this script installed
#
# No network calls, no telemetry. Requires Python 3.9+ for the scripts (standard library only).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME}/.claude/skills"
MODE="link"
ONLY=""
UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy) MODE="copy"; shift ;;
    --dest) DEST="$2"; shift 2 ;;
    --only) ONLY="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "install.sh: unknown option $1" >&2; exit 2 ;;
  esac
done

skills=()
for dir in "$REPO"/skills/*/; do
  name="$(basename "$dir")"
  [[ -f "$dir/SKILL.md" ]] || continue
  if [[ -n "$ONLY" && ",$ONLY," != *",$name,"* ]]; then continue; fi
  skills+=("$name")
done
[[ ${#skills[@]} -gt 0 ]] || { echo "install.sh: no skills matched" >&2; exit 1; }

if [[ $UNINSTALL -eq 1 ]]; then
  for name in "${skills[@]}"; do
    target="$DEST/$name"
    if [[ -L "$target" || -f "$target/.store-ready-kit" ]]; then
      rm -rf "$target" && echo "removed $target"
    elif [[ -e "$target" ]]; then
      echo "skipped $target (not installed by store-ready-kit)"
    fi
  done
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "warning: python3 not found; the skills' scripts need Python 3.9+" >&2
elif ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
  echo "warning: python3 is older than 3.9; the scripts may not run" >&2
fi

mkdir -p "$DEST"
for name in "${skills[@]}"; do
  src="$REPO/skills/$name"
  target="$DEST/$name"
  if [[ -e "$target" || -L "$target" ]]; then
    if [[ -L "$target" || -f "$target/.store-ready-kit" ]]; then
      rm -rf "$target"
    else
      echo "skipped $target: a different skill with this name exists" >&2
      continue
    fi
  fi
  if [[ "$MODE" == "link" ]]; then
    ln -s "$src" "$target"
  else
    cp -R "$src" "$target"
    cat "$REPO/VERSION" > "$target/.store-ready-kit"
  fi
  echo "installed $name -> $target ($MODE)"
done

echo
echo "store-ready-kit $(cat "$REPO/VERSION") installed. Restart your agent session, then try:"
echo '  "Audit my app before I submit it to the App Store."'
