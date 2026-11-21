#!/usr/bin/env bash
# Install all skills into every supported agent, with one command:
#
#   ./scripts/install-skills.sh
#
# Default user-level roots (3):
#   ~/.agents/skills   Codex, Cursor, Gemini CLI, Copilot CLI, Windsurf/Devin, OpenCode, DSH
#   ~/.claude/skills   Claude Code
#   ~/.copilot/skills  GitHub Copilot CLI
#
# Usage:
#   ./scripts/install-skills.sh [--dry-run] [--detected] [--copy] [--force]
#                               [--target agents,claude,...] [--uninstall]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"
MODE="link"
FORCE=0
DRY=0
UNINSTALL=0
DETECTED=0
SELECTED=""

log()  { printf '%s\n' "$*"; }
warn() { printf 'warn  %s\n' "$*" >&2; }
die()  { printf 'error %s\n' "$*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --copy)      MODE="copy" ;;
    --force)     FORCE=1 ;;
    --dry-run)   DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --detected)  DETECTED=1 ;;
    --target)    shift; [ $# -gt 0 ] || die "--target needs a value"; SELECTED="$1" ;;
    --target=*)  SELECTED="${1#*=}" ;;
    -h|--help)   sed -n '2,15p' "$0"; exit 0 ;;
    *)           die "unknown option: $1" ;;
  esac
  shift
done

[ -d "$SKILLS_DIR" ] || die "skills/ not found in $ROOT"

NAMES=()
while IFS= read -r name; do
  NAMES+=("$name")
done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)
[ "${#NAMES[@]}" -gt 0 ] || die "no skills found"

target_path() {
  case "$1" in
    agents)  printf '%s\n' "$HOME/.agents/skills" ;;
    claude)  printf '%s\n' "$HOME/.claude/skills" ;;
    copilot) printf '%s\n' "$HOME/.copilot/skills" ;;
    codex)   printf '%s\n' "$HOME/.codex/skills" ;;
    dsh)     printf '%s\n' "$HOME/.dsh/skills" ;;
    cursor)  printf '%s\n' "$HOME/.cursor/skills" ;;
    gemini)  printf '%s\n' "$HOME/.gemini/skills" ;;
    *)       return 1 ;;
  esac
}

TARGETS=()
if [ -n "$SELECTED" ]; then
  OLD_IFS="$IFS"; IFS=','
  for t in $SELECTED; do
    case "$t" in
      agents|claude|copilot|codex|dsh|cursor|gemini) TARGETS+=("$t") ;;
      *) IFS="$OLD_IFS"; die "unknown target: $t (use: agents,claude,copilot,codex,dsh,cursor,gemini)" ;;
    esac
  done
  IFS="$OLD_IFS"
else
  # Three roots cover every supported agent without duplicating a skill.
  TARGETS=(agents claude copilot)
fi

if [ "$DETECTED" -eq 1 ] && [ -z "$SELECTED" ]; then
  FILTERED=()
  for t in "${TARGETS[@]}"; do
    [ -d "$(dirname "$(target_path "$t")")" ] && FILTERED+=("$t")
  done
  [ "${#FILTERED[@]}" -gt 0 ] || die "no agent directory detected (run without --detected to create them)"
  TARGETS=("${FILTERED[@]}")
fi

run() {
  if [ "$DRY" -eq 1 ]; then
    log "dry-run: $*"
  else
    "$@"
  fi
}

if [ "$UNINSTALL" -eq 1 ]; then
  for t in "${TARGETS[@]}"; do
    target="$(target_path "$t")"
    [ -d "$target" ] || continue
    for name in "${NAMES[@]}"; do
      dest="$target/$name"
      if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$SKILLS_DIR/$name" ]; then
        run rm "$dest"
        log "unlinked $dest"
      fi
    done
  done
  log "done."
  exit 0
fi

# Validate the repository before touching the user's home directory.
python3 "$ROOT/scripts/check_skills.py" >/dev/null || die "check_skills.py failed; fix the repo first"

for t in "${TARGETS[@]}"; do
  target="$(target_path "$t")"
  [ "$DRY" -eq 1 ] || mkdir -p "$target"
  for name in "${NAMES[@]}"; do
    src="$SKILLS_DIR/$name"
    dest="$target/$name"

    case "$dest" in
      "$target"/*) ;;
      *) die "refusing to write outside target: $dest" ;;
    esac

    if [ -e "$dest" ] || [ -L "$dest" ]; then
      if [ -L "$dest" ]; then
        : # replace our own or another link
      elif [ "$FORCE" -eq 1 ]; then
        backup="$dest.bak.$(date +%Y%m%d%H%M%S)"
        run mv "$dest" "$backup"
        log "backed up $dest -> $backup"
      else
        warn "skip $dest (exists and is not a symlink; use --force)"
        continue
      fi
    fi

    if [ "$MODE" = "copy" ]; then
      run rm -rf "$dest"
      run cp -R "$src" "$dest"
    else
      run ln -sfn "$src" "$dest"
    fi
  done
  log "installed ${#NAMES[@]} skills -> $target"
done

if [ "$DRY" -eq 0 ]; then
  log ""
  log "done. Restart the agent (or start a new session) to pick them up."
  log "verify:   python3 scripts/check_skills.py"
  log "remove:   $0 --uninstall"
fi
