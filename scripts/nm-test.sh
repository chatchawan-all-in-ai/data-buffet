#!/usr/bin/env bash
# Usage, cached environment, and compile limits: document/how-to/run-and-debug.md.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/_nm-env.sh"
run_dir="$(mktemp -d)"
trap 'rm -rf "$run_dir"' EXIT

cd "$repo"
"$cli" --version
nm_compile > "$run_dir/compile.json"
node -e '
const g = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
const n = ["tables", "operations", "assertions", "declarations", "notebooks"]
  .reduce((s, k) => s + (g[k] || []).length, 0);
console.log("nm-test: dataform compile OK - " + n + " actions, 0 compilation errors");
' "$run_dir/compile.json"
