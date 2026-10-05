#!/usr/bin/env bash
# Usage, action selection, and dry-run limits: document/how-to/run-and-debug.md.
# CRLF is allowed because existing SQLX files use CRLF.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/_nm-env.sh"
run_dir="$(mktemp -d)"
trap 'rm -rf "$run_dir"' EXIT

all=0
[ "${1:-}" = "--all" ] && all=1
cd "$repo"

base=""
if [ "$all" = 0 ]; then
  base="$(git merge-base HEAD origin/dev 2>/dev/null || true)"
  [ -n "$base" ] || echo "nm-lint: no merge base with origin/dev, checking all actions"
fi

if [ -n "$base" ]; then
  git -c core.whitespace=cr-at-eol diff --check "$base" HEAD
  git diff --name-only --diff-filter=d "$base" HEAD > "$run_dir/changed.txt"
else
  git -c core.whitespace=cr-at-eol diff --check HEAD~1 HEAD 2>/dev/null || true
  : > "$run_dir/changed.txt"
fi
echo "nm-lint: git diff --check OK"

nm_compile > "$run_dir/compile.json"
if [ -n "$base" ]; then mode=changed; else mode=all; fi
"$python" "$repo/scripts/nm_dryrun.py" --compile "$run_dir/compile.json" --changed "$run_dir/changed.txt" --mode "$mode"
